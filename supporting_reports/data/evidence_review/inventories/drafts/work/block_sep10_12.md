# Incident inventory: block 2026-09-10 and 2026-09-12

Repo: `/media/projectspace/active-rail-refined-design-base` (read-only). Report paths are relative to `supporting_reports/`.

## Block overview

- 90 commits: `f562930` (Sep 10 05:10) through `75360cd` (Sep 12 21:15). There are no Sep 11 commits.
  - Phase A, endpoint reservoir: `f562930`..`2cd4244` (20 commits, Sep 10 05:10–09:34), 6 reports.
  - Phase B, electrothermal storage and work delivery: `0448351`..`7416b33` (19 commits, Sep 10 09:57–17:20), 5 reports.
  - Phase C/D, capacitor, joint support and scalar support: `5e59da3`..`f6a3e88` (12 commits, Sep 12 08:58–15:06), 9 reports.
  - Phase E, virtual radial cells: `49921aa`..`75360cd` (39 commits, Sep 12 15:43–21:15), 6 reports.
- All 26 reports work on the late, non-live endpoint patch x∈[-2.1,-0.5], s∈[0,1.285]. Six reports state that this patch carries 35.75% of the exchange weight. Each report says the shift and time derivatives of the scheduled metric stay active.
- None of the 26 reports mentions the Hawking–Ellis / Type IV classification. A grep for "type iv|hawking" finds 0 hits. Ten reports defer the negative-null remainder to an "independently supplied negative-stress sector" or a "quantum source". See counter-evidence C3.
- The `3dd210f` hash named in the task is a Sep 16 commit, "Record conserved-material reconfiguration…", so it falls outside this block. The interruption commit in this block is `3dbd12b`.

---

## I1. Numerical temperature floors misread as physical heat depletion (merged: elastic, EM and conductor stops)

- **Date/commits:** Sep 10. `f562930`, `38ea61b` (elastic). `9f1429c`, `a107821`, `56e6b8d` ("electromagnetic heat-verification barrier"). `148b5eb` ("resolve near-cone inversion conditioning").
- **What happened:**
  - Elastic, uniform initial stretch: runs stopped at s=0.948–1.022. The zero-exchange controls also lost positive temperature, at s=0.925 and 0.955, although the exact adiabatic law conserves each element's heat. The report concludes: "Their temperature floor is therefore a numerical limitation" (ELASTIC_ENDPOINT_STORAGE_INVESTIGATION.md:141-147).
  - EM field storage: the ideal zero-exchange control drove an element from q=0.48221 to zero heat at s=0.03702, with a zero continuum right-hand side (ELECTROMAGNETIC_ENDPOINT_STORAGE_INVESTIGATION.md:196-204). "Global conservation of the combined tensor leaves that internal-energy error undetected" (:203-204).
  - The 512-cell resistive stop at s=0.21472 disagrees with the element's heat budget by 2.12367 (:207-212).
  - The ratio-1 stop "moves comparatively little between 256 and 512 cells", yet it keeps a heat discrepancy of 0.14090 against an initial 0.26104. "Convergence of a stopping time alone would therefore give an incorrect impression of a physical limit" (:214-218).
  - Conductor replay: 3 of 5 finite-speed runs stopped at a primitive-inversion limit while "still inside the analytic causal boundary" (ACTIVE_RESERVOIR_CAUSAL_TRANSPORT.md:259-266). With 64 safeguarded iterations they reached the constitutive causal boundary instead.
- **What detected it:**
  - Source-free (zero-exchange / ideal) controls whose continuum law conserves heat.
  - An independent Lagrangian heat audit along material labels.
  - For the conductor runs, a comparison of the stop state with the analytic boundary.
- **When the detecting knowledge became available:** textbook. Recovering internal energy as a small difference of large conserved totals is the known failure that the dual-energy formalism (Ryu et al. 1993; Bryan et al. 1995) addresses. Primitive-variable recovery at high Lorentz factor is known to be ill-conditioned (e.g. Noble et al. 2006).
- **Counterfactual:** these checks were cheap and were run in the first comparison round, so this is largely a check that caught a problem early. The EM branch still spent 25 runs (about 10.3 MB) before stopping at the "verification barrier" (:223). A variational material-coordinate scheme (`1fdf48e`, `8880934`) removed the collapse: "The previously observed zero-exchange temperature collapse is removed" (ACTIVE_RESERVOIR_ENSEMBLE_REFINEMENT.md:170-172).
- **Cost:** about 4 commits and 1 report section (EM storage) ended at a numerical barrier with no physical verdict.
- **Candidate lesson:** in any forced-matter or source simulation on a metric, run a source-free control that the continuum law says preserves the quantity at issue. Classify every stop as numerical or physical before interpreting it. A converging event time is not evidence that the event is physical.
- **Generality:** general to numerical source modelling in any spacetime design. It is close to a truism in computational fluid dynamics, but the "stop-time converges ⇒ physical" trap is specific and worth teaching.
- **Recurrence in block:** 3 (elastic floors, EM floors, conductor inversion limit).

## I2. Energy error normalized to the wrong budget; time-step control inactive under CFL (`8880934`)

- **Date/commit:** Sep 10, `8880934` ("expose time-integration accuracy").
- **What happened:**
  - The canonical-energy errors were "near 0.5 against initial energies around 34,700", about 1.4e-5 relative, while the decisive local heat values are about 0.25.
  - "Reducing the maximum step alone leaves much of it because the material-wave step restriction is already controlling" (ACTIVE_RESERVOIR_ENSEMBLE_REFINEMENT.md:183-190). Tightening the Courant factor from 0.2 to 0.05 cut the error to 0.009092, "approximately sixtyfold" (:194-195).
  - Spatial refinement then exposed 55.5% and 47.6% RMS differences in density and radial stress between 64 and 128 cells (:202-205). Of the squared error, 97.6% (density) and 99.6% (radial stress) lie in the end regions (:376-379), where undamped compression fronts form.
- **What detected it:** an independently recomputed canonical energy, compared against integrated geometric and endpoint power, plus a spatial refinement pair.
- **Available earlier:** yes. Two points are standard knowledge:
  1. An error budget should be normalized against the smallest quantity that decides the outcome, here local heat.
  2. Nonlinear hyperbolic material without dissipation steepens into fronts, so pointwise stress does not converge without an entropy-consistent scheme.
- **Counterfactual:** normalizing the ledger by the minimum local heat, and giving the Courant factor as a separate refinement axis, would have exposed this at the first run.
- **Cost:** small, about 2 commits. The unresolved end-region stress was carried as an open gate.
- **Candidate lesson:** give conservation errors relative to the smallest budget that decides pass/fail, not to total energy. When refining in time, check which step restriction is actually active.
- **Generality:** general numerics, fairly textbook.
- **Recurrence:** 2. GRADED also shows force concentration growing under refinement (see I13).

## I3. Chasing heat-delivery symptoms of a mechanical root cause (γ≈47 material); redirected by the user's velocity concern

- **Date/commits:** Sep 10.
  - Symptom-treatment chain: `9f1429c` → `56e6b8d` (EM storage), `1fdf48e` → `efb2bf4` (ensemble plus relaxation), `d59e422` → `4f3eb03` (causal conduction).
  - Redirection: `6b6433b`, `ecab6c2`, `c0426ec`, `aa22156` (prestressed backbone).
- **What happened:** after the elastic reservoir depleted locally, three consecutive reports added heat supply: EM storage, strain relaxation and finite-speed conduction.
  - The depleted element moves at v=−0.999484 with n_eff=1.05e-3 and q̇_endpoint=−31.04. The conversion channels replace only 0.91% of that withdrawal (ACTIVE_RESERVOIR_ENSEMBLE_REFINEMENT.md:344-358). The mechanism is explicit in `q̇_endpoint = αR²(−P+vF)/(A n_eff)` (:364).
  - The null cone's upper material edge contracts to f=0.5000053 at release (ACTIVE_RESERVOIR_CAUSAL_TRANSPORT.md:120-122), so neighbouring warm material cannot reach the cold element causally.
  - The best conductor keeps only 0.00446 heat (0.153% of 2.91448). It needs 13.77 units of positive mechanical work and a force of 36.13 (:7, :289-356).
  - The prestressed report then shows that the extreme speed is a property of the soft support: "The near-light-speed material history therefore depends strongly on the tested mechanical construction" (PRESTRESSED_BUFFER_VELOCITY_INVESTIGATION.md:13-14). It also says, "Increasing thermal conductivity around the earlier near-light-speed trajectory would leave this mechanical question unresolved" (:340-342).
  - The report records "the user's material-velocity concern" (:237) and the prior cold-element Lorentz factor "near 47" (:174).
- **What detected it:** the user's concern about material velocity, followed by a force and kinematic audit.
- **Available earlier:** yes. Material speeds were tabulated from the first report: 0.9342 (ELASTIC_ENDPOINT_STORAGE_INVESTIGATION.md:244) and 0.9743 (ELECTROMAGNETIC…:162). The 1/n_eff factor in the forced heat equation was visible from the start.
- **Counterfactual:** a per-element Lorentz-factor and dilution diagnostic in the first elastic run would have pointed at the load path before any heat-supply add-ons. Cost to add: one column in the output.
- **Cost:** about 8–10 commits and parts of 3 reports (EM storage, ensemble, causal transport), roughly 2.5 h of Sep 10 morning. The replacement assembly was itself set aside 1 h later (I4).
- **Candidate lesson:** when a prescribed or fitted exchange tensor is imposed on dynamical matter, first check the kinematics of the receiving matter (γ, dilution, causal access). A local deficit that scales as 1/n_eff comes from the load path or the one-way coupling. Adding stores or conductors does not fix it.
- **Generality:** applies to any metric-engineering workflow that forces a demanded tensor onto a trial material with one-way coupling. The exact 1/n mechanism is specific to this forced-exchange setup.
- **Recurrence:** 1 chain of 3 reports.

## I4. Source-compatibility (null-projection) check performed after the dynamics; prestressed reservoir set aside by the user (`21b98b9`, `2cd4244`)

- **Date/commits:** Sep 10. `a60432b` and `21b98b9` (audit), then `2cd4244` ("Set aside the prestressed reservoir and record physical source-selection priorities").
- **What happened:**
  - The slower prestressed assembly (peak speed 0.63–0.67) needs 8.1× the prior initial energy. Its startup peak density and radial stress are 646× and 1619× the prior peaks (PRESTRESSED_BUFFER_VELOCITY_INVESTIGATION.md:9, :255).
  - The feasibility audit found a required negative radial-null contribution of 14.21 at startup and 75.78 at fade. The geometric radial-null stress is 0.00437 and 0.0210, so the startup figure is "about 3248 times that geometric comparison" (RESERVOIR_FEASIBILITY_ENVELOPE.md:139-148).
  - Every sampled node requires negative contribution from the remaining source.
  - Optimizing over the preload family lowers the burden only about 23%, to 10.90 (:180-194).
  - An exact identity ties the burden to buffer inertia and bulk motion: `max_± S_kk = w_b/(1−c_f²)·(1+|v|)/(1−|v|)` (:207-215).
  - The user then set the assembly aside and deferred string and string-cloud sources (:257-260; new SOURCE_CONSTRUCTION_SELECTION.md).
- **What detected it:** computing the full remaining source D−M−S and its projections on the radial null vectors k±.
- **Available earlier:** yes, as textbook NEC bookkeeping. Any sector that satisfies NEC contributes k·T·k ≥ 0, so adding positive-energy support raises the negative remainder required elsewhere. The report states this itself: "Contributions from further positive-energy supports can increase the negative-source requirement" (:164-165). The (1+|v|)/(1−|v|) factor is the Doppler weight of a boosted null projection.
- **Counterfactual:** evaluating k·S·k of the proposed initial reservoir tensor, one tensor evaluation per node, before registering any dynamics would have shown the burden. This ran 20 commits and about 4.3 h after `f562930`. Even the older thermal assembly already needed 0.0132 at startup and 4.656 at s=0.815 (:196-201).
- **Cost:** Phase A as a whole: 20 commits, 6 reports and about 4.5 h, set aside. This includes the causal-transport and prestressed dynamics that the null-projection gate made moot.
- **Candidate lesson:** in a geometry that requires NEC violation, screen each proposed support component by its null projections, including those from its bulk velocity, before designing its dynamics. Positive-energy supports can only increase the exotic remainder.
- **Generality:** universal for NEC-violating metrics (warp, wormhole, shift-driven). It is close to a truism, but was repeatedly applied late.
- **Recurrence:** 4. RESERVOIR_FEASIBILITY:164; REGENERATIVE_CONVERTER_EVALUATION.md:182-185 ("Any additional component with nonnegative null projection increases…"); GRADED_ELECTROTHERMAL_ASSEMBLY.md:383-385; COMPOSITE (retained co-moving energy raises holding force).

## I5. HiGHS silently dropped small active-metric coefficients; solver status contradicted feasible-set nesting (`1b70929`), and later "valid" native states violated the original rows

- **Date/commits:** Sep 10 `1b70929` ("audit dropped solver coefficients"); Sep 12 `c05aa05` and `5dc7ce4` (native-state rejection).
- **What happened:**
  - The heat-engine control was reported infeasible, although its constraints include every direct-work history and a direct-work history had succeeded on the same grid.
  - Substituting that history into the heat-engine problem gave a scaled equality residual of 9.45e-9 and an inequality violation of 1.29e-14 (PRESSURE_LINKED_STORAGE_COMPLETION.md:223-228).
  - Cause: "HiGHS deletes coefficients at or below 1e-9 by default". "The large volume-weighted stores can give small shift coefficients a measurable product" (:230-237).
  - With the threshold at 1e-12, the heat-engine control became feasible (peak null 5.60987). The other infeasible statuses stood (:241-252).
  - Sep 12: a native HiGHS candidate marked valid with zero primal infeasibility had an original equality residual of 0.5094 and an inequality excess of 7.9125, and was rejected (VIRTUAL_RADIAL_CELL_PRESSURE_LINK_REALLOCATION.md:527-536). Interior-point candidates with violations of 0.00156 and 0.00122 were likewise rejected (VIRTUAL_RADIAL_CELL_PASSIVE_PHOTON_CLOSURE.md:228-233, :276-279).
- **What detected it:** a logical check. A relaxation cannot be infeasible when a tighter problem is feasible. Candidates were then substituted into the original, unscaled matrices.
- **Available earlier:** yes. The option is documented by HiGHS, and checking optimizer output against the original constraint rows is standard linear-programming practice.
- **Counterfactual:** substituting known-feasible points into every nested relaxation costs essentially nothing. It could have run from the first HiGHS use (`37f69f0`, 1 h earlier).
- **Residual gap:** the fix went forward only. `toolkit/adm_harness_cli/adm_harness/graded_electrothermal.py:142-145` (`solve_linear_program`) still calls `linprog` without `small_matrix_value`. The GRADED results from `0448351` to `37f69f0` were not rerun, including "Two cases encountered a numerical failure" and three time-limited programs (GRADED_ELECTROTHERMAL_ASSEMBLY.md:164-166, :226-227). Their retained optima do carry separate reconstructed-tensor residual checks.
- **Practice improvement within the block:** by Sep 12, infeasibility claims came with Farkas-type certificates reduced to 30 inequalities and checked in exact rational arithmetic. JOINT_SUPPORT_CONSTRUCTION_REVIEW.md:130-145 gives `0 ≤ −0.00176574`. SCALAR_FLUX_SUPPORT_CONSTRUCTION.md:195-209 gives −0.000485543 and −0.000571242.
- **Cost:** small, 1 commit. One control outcome reversed, from infeasible to feasible.
- **Candidate lesson:** in optimization-based source design on badly scaled metric data, where tiny lapse or shift derivatives multiply large stores, never read a solver's "infeasible" or "optimal" status as physics. Check nested-relaxation consistency and the original rows, and require certificates for infeasibility.
- **Generality:** general to inverse and LP-based spacetime or source engineering. The specific HiGHS default is a tooling detail.
- **Recurrence:** 4 (1b70929; native state 0.5094; IPM candidates 0.00156 and 0.00122; unresolved statuses around THERMAL_EXCHANGE:246).

## I6. Local storage must hold energy comparable to its own rest energy: the mass barrier recurs four times

- **Date/commits:** Sep 10 `64006ae` ("reject the benchmark local bank"), `7416b33`. Sep 12 `5e59da3`, `41a074a`, `75360cd`.
- **What happened:**
  1. Capacitor bank benchmark: Eaton XL60, 26,213.6 J/kg, which carries 3.43e12 units of rest energy per unit stored (REGENERATIVE_CONVERTER_EVALUATION.md:169-171).
     - Necessary negative null: 1.9e11 against the prior 0.104 estimate, "about 1.8 trillion times" (:8, :176-187).
     - Break-even needs 5.3e16 J/kg, about 0.6 c² (:200-206).
  2. The allowed added capacitor material is about 0.401× the rated energy, which corresponds to 2.24e17 J/kg, about 2.5 c² (FINITE_WORK_INTERFACE.md:155-163, :219-221).
  3. Electron/positron charge layers need ≥5.10 MV, above the 1.022 MV pair threshold (CHARGED_CAPACITOR_CONSTRUCTION.md:280-292).
  4. Radial-cell thermal bank after the full Phase E thermal program: absorbed cold-bank heat requires a specific-energy increment of 7.1–9.3 c² (first location) and 3.1–6.3 c² (second) (VIRTUAL_RADIAL_CELL_PHOTON_CONTACT_DESIGN.md:12-20, :211-217). "The constant-capacity comparison makes a general material search premature … Work pauses at this checkpoint" (:271-274).
- **What detected it:** adding the rest mass of the store to the source comparison, or charging it to the spare density budget.
- **Available earlier:** trivially. Ordinary electrical, chemical and thermal stores hold about 1e-12 to 1e-10 of their rest energy (E/mc²). The block itself established this for capacitors on Sep 10 at 15:04.
- **Counterfactual:** once a component's heat or work duty per label (about 0.09–0.11) and the spare density or rest inventory (0.011–0.035 per label) are known, the ratio takes one line. Phase E defined those duties at `4d6af24` / `cc1c210` (Sep 12 17:47 / 18:28). The next 22 commits and 3 reports (PRESSURE_LINK_REALLOCATION, PASSIVE_PHOTON_CLOSURE, PHOTON_CONTACT_DESIGN) developed temperatures, contact coefficients, photon turnover and junctions before the ratio closed the branch. The radiation-bank caloric law used meanwhile avoided rest mass by needing cold/hot volume contrasts of 2.68e19 and 4.69e21 (PRESSURE_LINK_REALLOCATION.md:251-252), and later 6.6e7.
- **Cost:** Phase E thermal sub-branch: about 22–25 commits, about 3 h and 3 reports, paused at the mass requirement. Sep 10: 2 commits for the capacitor.
- **Candidate lesson:** in metric engineering, local support components exchange energy of the same order as the geometry's source scale. Screen every store, reservoir or bank by E_stored/(M c²) against the available density budget before developing its transport or thermodynamics. Only field- or radiation-dominated stores can pass, and those then need their own containment stress (see I7).
- **Generality:** very general for designs whose demanded stresses are O(ρc²) in geometric units. The specific ratios are design-specific.
- **Recurrence:** 4 in the block.

## I7. An optimistic enclosure bound (U/3 trace) served as the selection reference after a 3× tighter bound was derived

- **Date/commits:** Sep 10 `64006ae` (bound introduced), `7416b33` (componentwise bound derived). The reference was used through Sep 12 `5e59da3` / `371bdf9` / `0e07a9c`.
- **What happened:**
  - The regenerative evaluation assigned wall energy `(bank_capacity+heat_capacity)/3` from the stress-trace bound (REGENERATIVE_CONVERTER_EVALUATION.md:88-93). This gave the "formal enclosure" fade requirement of 0.262788 (:212-214).
  - Two hours later FINITE_WORK_INTERFACE derived that DEC applied componentwise requires wall energy ≥U, not ≥U/3, so the cell carries ≥2U in total. It calls this "stronger than the U/3 trace bound" (FINITE_WORK_INTERFACE.md:224-235). Counting the adiabatic wall work raises the fade requirement to 0.5338 (:246-254).
  - The old 0.262788 still served as the comparison reference in the POYNTING break-even table (POYNTING_WORK_DELIVERY.md:240; FINITE_WORK_INTERFACE.md:38, :106, :160).
  - CHARGED_CAPACITOR preserves "the earlier formal fade reference 0.262788" (:36-38). It judged magnetic insulation at 0.25405 "below the previous formal reference … would look favorable" (:204-206).
  - COMPOSITE finally demotes it: "The older 0.262788 formal-store value is an assembly comparison, with no universal feasibility status" (:158-159).
- **What detected it:** re-deriving the equilibrium stress integral for an aligned field, with per-principal-stress DEC.
- **Available earlier:** yes. The von Laue theorem / virial theorem for self-stressed static systems (cited: Giulini) and the virial mass bound for magnetic and capacitive energy storage (e.g. SMES, M ≥ ρE/σ) are textbook. The same citation was already in REGENERATIVE (:84-87).
- **Counterfactual:** applying the componentwise bound at `64006ae` would have doubled or tripled the enclosure baseline before it anchored about 6 commits of comparisons.
- **Cost:** modest. No decision reversed outright, but the break-even and "apparent advantage" framings in 3 reports were relative to a baseline known to be optimistic.
- **Candidate lesson:** when a bound becomes a selection reference, use the tightest cheap necessary bound: componentwise energy conditions and the virial/Laue integral, not trace bounds. Re-baseline explicitly when a tighter bound appears.
- **Generality:** general for any design that sizes containment for field-energy stores.
- **Recurrence:** 1 bound, reused in 4 reports.

## I8. Partial ledgers gave apparent advantages; counting the coupled route reversed them (merged: magnetic insulation, internal capacitor closure, relaxed local gates)

- **Date/commits:** Sep 12 `5e59da3` / `371bdf9` (capacitor insulation), `0e07a9c` / `162f399` (composite), Phase E `4d6af24` → `27f8f18`.
- **What happened:**
  - Magnetic insulation of the capacitor looked favorable at 0.25405 from the instantaneous tensor. Sending its work through the receiver route raised the fade requirement to 8.640 (null-field limit) up to 43.501 (insulation speed 0.5) (CHARGED_CAPACITOR_CONSTRUCTION.md:230-239). Guide flux rose from 0.66966 to 90.88, and startup energy to about 74,456 (:247-251). "Counting its transport through the selected receiver route removes the apparent source advantage" (:8-9). The physical cause is textbook: with frozen flux, B∝1/area, so transverse magnetic energy rises under the scheduled compression (:255-262).
  - An internally balanced capacitor cancels the electric stresses that the pressure-link force balance relied on. The required pressure drop is 0.03775 against 0.00586 available, 6.45× (COMPOSITE_CAPACITOR_AND_RAIL_CONNECTIONS.md:11-16, :290-297).
  - A radial-cell local LP with phase-only relaxation cleared both locations. Restoring coherent finite-cell control and causal work delivery re-opened a deficit of 0.00293618 (VIRTUAL_RADIAL_CELL_THERMAL_EXCHANGE.md:3-8, :272-277).
- **What detected it:** each time, counting the omitted coupled transport, reaction or coherence constraint.
- **Available earlier:** yes. Flux freezing and field compression work are textbook electrodynamics. A load-path stress cannot be removed from a force balance by packaging it without replacing it.
- **Counterfactual:** a cheap sign/order-of-magnitude estimate of the compression work, dU_B = U_B·d ln(1/area), would have flagged the insulation option before the transport run. Cost: 1 formula.
- **Cost:** about 2 commits (insulation), about 2 commits (composite) and about 3 commits (thermal relaxation). Each was stopped within the same day.
- **Candidate lesson:** compare candidate components by their complete assembly ledger, including transport of their work, reactions and heat along the actual route. Instantaneous or local tensor comparisons systematically flatter the candidate. A field that carries load cannot be re-packaged as an isolated store without replacing its stress.
- **Generality:** general across source and component engineering.
- **Recurrence:** at least 4 (insulation, internal closure, relaxed thermal LP, and the pressure column in I9).

## I9. Local contact cost versus connected pressure column: exponential self-weight in a strong lapse gradient (`13cbdd1`, `152e32e`)

- **Date/commits:** Sep 10 `13cbdd1`, `152e32e` ("Record the pressure-link preload cost").
- **What happened:**
  - GRADED sized three local fluid pressure pieces at 158.34 (startup) and 16.69 (fade) slice energy. Their loaded ends were left as "explicit pressure-transmission requirement[s]" (GRADED_ELECTROTHERMAL_ASSEMBLY.md:308-360; slice energies at :354-357).
  - Connecting them into one column, with `p_x + 4ΓB a_s p = ΓB F_required`, requires a peak pressure of 221,216.7 and slice energy 30,913,090 at startup, and 56.42 and 7,015.13 at fade. "The integrating factor accumulates that self-weight across the large clock gradient" (PRESSURE_LINKED_STORAGE_COMPLETION.md:113-128). The ratio at startup is about 2e5.
  - An analytic integrated witness (I=−2.1946573 with positive K) then proved that balanced ends are impossible, so a terminal reaction is required (:148-173).
- **What detected it:** integrating the connected hydrostatic equation.
- **Available earlier:** yes. In GR, pressure contributes inertia ((ρ+p)a), so a column supported against a lapse gradient needs pressure growing like exp(∫(κ+1)ΓB a dx) (Tolman / TOV-type hydrostatics). The patch's radial scale varies from about 6 to 465 at s=0 (ELASTIC_ENDPOINT_STORAGE_INVESTIGATION.md:149-153).
- **Counterfactual:** evaluating the integrating factor exp(∫4ΓB a dx) across the patch, one quadrature, when the local pieces were proposed would have shown the scale immediately.
- **Cost:** about 2 commits. The joint redistribution and bidirectional conversion later recovered a low-burden history (0.0937). The local-piece cost estimate was superseded.
- **Candidate lesson:** for any pressure- or stress-transmitting member in a strongly varying lapse, estimate the GR self-weight integrating factor before sizing local pieces. Loads left as "end requirements" hide exponential costs.
- **Generality:** general to static support in strong gravitational or redshift gradients, a textbook result. The numbers are design-specific.
- **Recurrence:** 1, related to I8.

## I10. Moving-frame electromagnetic force omitted in the independent audit (`9133810`, explicit correction)

- **Date/commit:** Sep 12 11:01, `9133810` ("Correct the moving-frame electromagnetic force in the support audit"). This is 20 min after `b368552` introduced the audit.
- **What happened:**
  - The independent continuum audit (`scripts/audit_joint_support.py` at `b368552`, line 73) computed `field_force=-(field_x-share_x)/(ell*radius**4)`. It omitted the temporal electric momentum term `−v H_t/(N R^4)` that arises from `F_rest = Γ(F_normal − v P_normal)` (JOINT_SUPPORT_CONTINUUM_CORRECTION.md:3-17).
  - The solver target already contained it (:5-6), so the auditor was wrong and the solver was right.
  - The original report claimed the audit's formulas "pass an independent normal-frame covariant-divergence test on a metric with nonzero shift and time-dependent lapse…" (JOINT_SUPPORT_STRESS_SCHEDULE.md:211-213). That test (`tests/test_joint_support_audit.py` at `b368552`, line 45) set `flux_energy=zero`, so the field term was never exercised. The new test's docstring says: "the earlier manufactured material-only audit could not detect the missing boost term".
  - Numerical effect: 11.96%→11.893%, 9.75%→9.831%, 8.24%→8.181%, and the lifted composite 4.60%→4.497% (STRESS_SCHEDULE.md:217-219, :232; CORRECTION.md:22-26, :34-36). Solved schedules, source remainders and end-work figures are unchanged (:40-43). The diff to STRESS_SCHEDULE.md adds only a 5-line supersession header (lines 3-6).
- **What detected it:** not recorded. The fix adds a manufactured test with a time-dependent field and nonzero material velocity, and verifies it against an independently differentiated covariant divergence.
- **Available earlier:** yes. The boost projection of four-force is textbook special relativity.
- **Counterfactual:** a manufactured solution exercising every source term (nonzero H_t, nonzero v) at audit creation would have caught it at once.
- **Cost:** 1 commit and 1 short erratum report, with 5 audits recomputed and 264 hashes. No decision changed.
- **Candidate lesson:** a verification test only verifies the terms it activates. Manufactured solutions must switch on every coupling (time dependence × velocity × field), especially for frame projections where cross terms vanish in static tests.
- **Generality:** general (method-of-manufactured-solutions coverage).
- **Recurrence:** 1 explicit erratum. The pattern also shows up in counter-evidence C1.

## I11. Selected composite-support target reversed by conservative evolution: collocation-only satisfaction hid inadmissibility

- **Date/commits:** Sep 12 `b368552` ("Identify a regulated composite-support target", 10:41) was superseded by `a986c28`, `9a5f0be` and `ad2e7f7` (13:31).
- **What happened:**
  - Selected target: fade negative-null remainder 0.33291 (1.63× the 0.2038 reference) and initial support energy 1,271.66 (JOINT_SUPPORT_STRESS_SCHEDULE.md:112-125). The solver residual was 3.24e-12, but the continuum audit gave an 8.24% force residual in the same commit (:204, :215-224).
  - Joint midpoint inverse: 15.23% force and 20.37% power residual at 32 cells (JOINT_SUPPORT_CONSERVATION_AND_PASSIVITY.md:87).
  - Conservative implicit evolution: "An admissible approximate tensor becomes inadmissible when its force balance is evolved more accurately". The member density deficit stays at 0.5748–0.5778 under both spatial and temporal refinement (JOINT_SUPPORT_REFINEMENT_AND_END_LOADS.md:4-7, :72-79).
  - Final conserved routed target: initial inventory 7952.49 / 7914.71 against 2297.42, material null peak 1.656–1.765 against cap 0.2, and fade remainder 3.18149 (JOINT_SUPPORT_CONSTRUCTION_REVIEW.md:41-44, :73-78, :156-160). That is about 9.6× the selected 0.33291. "Accurate work accounting and momentum balance place a substantially larger load on the support than the early approximate tensor suggested" (:5-7).
- **What detected it:** a dense independent quadrature audit between solver points, followed by conservative time evolution and energy reconstructed from counted work.
- **Available earlier:** at `b368552` itself. The 8–12% residuals were already measured when the target was "identified".
- **Counterfactual:** a promotion rule (continuum residual ≲1% and member energy admissible between nodes) would have kept the candidate from being labelled a target.
- **Cost:** about 4 commits and about 3–4 h. The selected target was reversed, and the burden rose by about an order of magnitude.
- **Candidate lesson:** an inverse-designed stress schedule enforced only at samples or collocation points is not a supplied continuum source. Tiny discrete residuals are uninformative. Promote a schedule only after a dense conservation audit and an admissibility check between nodes.
- **Generality:** general to inverse/source design on any metric.
- **Recurrence:** see I12. In total the between-samples lesson appears about 7 times in the block.

## I12. Clearances that existed only at sample points or at a moved test location (virtual radial cells)

- **Date/commits:** Sep 12 `79b92d1` → `7eca71b` ("expose transient overloads") → `5136697` → `716778c` ("record failure under finer wave replay") → `52021bc` → `183f925`; then `ae538ae` ("Resolve true midpoint stress") and `9dbaf92` ("Correct endpoint thermal bounds").
- **What happened:**
  - Narrow pairs at x=−1.9875 cleared with zero added density, but "the narrow pairs sit between the earlier startup witnesses" at x=−2 and −1.975 (VIRTUAL_RADIAL_CELL_CONSTRUCTION.md:170-193).
  - At the witnesses, independent explicit SSP-RK2 replay withdrew the implicit optimizer's clearances, with deficits 0.001617 and 0.014184 (:207-223).
  - The exponential scheme passed replay at 48×1029, then failed at 96×2057 with brief overloads between samples of 0.0011494 and 0.0010623 (:246-252).
  - The fix was positive supersolution ceilings bounding the wave over whole panels. Final margins were 9.75e-5 and 6.24e-5 (:357-393).
  - Later, the thermal pilots were rejected by curved replay: full-density shortfalls of 0.01009 and 0.02173. "At the two worst samples, the exact radial stress differs from the endpoint-averaged target by +0.0102620 and −0.0212212" (VIRTUAL_RADIAL_CELL_PRESSURE_LINK_REALLOCATION.md:337-356).
  - Midpoint-only temperature coefficient selections "fail the tighter temperature bound at a known time knot". Correcting this raised the volume-contrast infimum from 1.53e6 / 3.07e6 to 7.2e6–8.4e6 (VIRTUAL_RADIAL_CELL_PASSIVE_PHOTON_CLOSURE.md:466-496).
  - Related: potential optima exceed available energy between nodes by 0.00066875 and 0.00084963 (SCALAR_FLUX_SUPPORT_CONSTRUCTION.md:144-147). Force quadrature has to split at quintic allocation knots (JOINT_ELASTIC_BACKING_PRESSURE_SCREEN.md:185-187; POYNTING_WORK_DELIVERY.md:196-198).
- **What detected it:** independent replay at higher temporal and spatial resolution, and exact midpoint stress from the registered geometry.
- **Available earlier:** yes. Enforcing constraints over intervals (maximum-principle / supersolution envelopes, or evaluating the true target inside panels) is standard for time-dependent constraints.
- **Counterfactual:** envelope constraints and exact in-panel targets from the first transport and thermal solves, and keeping known witness locations inside every narrowed test domain.
- **Cost:** about 6 commits (transport) plus about 3 (averaging and midpoint), roughly 2 h. Several "clearances" were withdrawn.
- **Candidate lesson:** for time-dependent operation on a changing metric, enforce the stress/energy budget over whole intervals, not at samples, and never average the demanded tensor over a panel. When shrinking a test domain, keep the previously failing witness inside it.
- **Generality:** general numerics for scheduled or time-dependent metric designs.
- **Recurrence:** about 7 across the block (counted with I11).

## I13. Optimizers exploit thermodynamically unphysical freedoms; passivity audited after the fact

- **Date/commits:** Sep 10 `aef46c7` / `16e7cd3` (graded), Sep 12 `1e5076a` (joint elastic), `a35adb8` / `183f925` (cycling), `91e2bc9` → `c053db9` (receiver temperatures).
- **What happened:**
  - Graded inverse: under refinement, peak contact force density doubles from 0.10891 to 0.21843 and effective conductivity from 174.6 to 342.1, because "The optimizer concentrates the force inside the allowed band" (GRADED_ELECTROTHERMAL_ASSEMBLY.md:176-184).
  - Joint elastic: optimized heat schedules "fail a simple passive contact test at every sampled material label". Warm→fluid and fluid→warm capacity intervals have empty intersection (JOINT_ELASTIC_BACKING_PRESSURE_SCREEN.md:149-156).
  - Virtual cells: "large simultaneous conversion cycles, which use the converter losses to export heat" (VIRTUAL_RADIAL_CELL_CONSTRUCTION.md:291-296), removed by control reconstruction.
  - Receiver: the inventory-minimized fluid goes near-cold, needing α⁴>124.95 and <1.694e-16 at one sample (PRESSURE_LINK_REALLOCATION.md:200-209, α⁴ bounds at :204-205), and photon volume contrasts of 2.68e19 and 4.69e21 (:250-254). A warm floor reduced this "by more than thirteen orders of magnitude" (:286-288).
- **What detected it:** post-hoc passivity, temperature-ordering and regularity audits.
- **Available earlier:** yes. The second law (Clausius ordering), no simultaneous forward/reverse conversion, and regularity or finite-rate constraints are textbook.
- **Counterfactual:** writing passivity and regularity into the optimization from the start. They are linear or simple convex constraints, as later done with bank routing rows (PASSIVE_PHOTON_CLOSURE.md:203-213).
- **Cost:** several audit-then-reoptimize loops, about 6–8 commits.
- **Candidate lesson:** energy-momentum balance alone admits schedules that no passive material can realize. Inverse source design must carry thermodynamic (second-law, passivity) and regularity constraints, or its optima sit on unphysical boundaries.
- **Generality:** general to inverse design with energy-exchange freedoms.
- **Recurrence:** 4–5.

## I14. Spatial march posed against the characteristic direction (`a986c28`)

- **Date/commit:** Sep 12, `a986c28` ("Reject unstable and energetically inadmissible fixed-history projections").
- **What happened:** "The first spatial march uses the left pressure history. Its errors grow rapidly with refinement, reaching an unusable amplified solution. Here the coefficient of the temporal pressure derivative has the sign of the material velocity, which lies between approximately −0.202 and zero. Reversing the radial orientation places the prescribed pressure history at the incoming right cut and removes that numerical blow-up" (JOINT_SUPPORT_CONSERVATION_AND_PASSIVITY.md:56-61). The incoming-boundary version still failed physically: member deficit 0.478 and residuals 10.8% / 5.12% (:63-68).
- **What detected it:** refinement blow-up.
- **Available earlier:** yes. Well-posedness of hyperbolic/transport problems requires data on inflow characteristics, and marching sideways or backward is ill-posed. This is textbook.
- **Counterfactual:** checking the sign of the characteristic speed before choosing the marching boundary.
- **Cost:** 1 projection run within one commit.
- **Candidate lesson:** in a moving material frame on a shifted metric, the inflow boundary is set by the characteristic direction, and that depends on the material velocity. Prescribe data there.
- **Generality:** general PDE practice. It matters most in metric engineering because shift and material drift flip characteristic directions.
- **Recurrence:** 1. The follow-up implicit evolution "from the incoming cut" (JOINT_SUPPORT_REFINEMENT_AND_END_LOADS.md:62-67) reused the fix.

## I15. The demanded stress changes character over the cycle, which excludes passive or permanent prestress (cheap nodewise checks caught it)

- **Date/commits:** Sep 12 `b368552`, `a986c28`, `15bb755`, `f6a3e88` ("certify the graded-vortex barrier").
- **What happened:**
  - 73.6% of the composite's absolute axial-force changes run opposite to passive-spring behaviour (JOINT_SUPPORT_STRESS_SCHEDULE.md:140-146).
  - The coupled convex-energy screens fail: 77.4% of the gradient/stretch product is negative and 80.6% of supporting-plane pairs fail. All 4 LPs are infeasible (JOINT_SUPPORT_CONSERVATION_AND_PASSIVITY.md:24-36).
  - A permanent flux-tube bundle requires A≥2.02361 at one node and A≤0.00237834 at another, "a factor of about 851" apart (SCALAR_FLUX_SUPPORT_CONSTRUCTION.md:87-93). Arbitrary time-independent grading is also infeasible, with rational certificates (:185-209).
  - Causal elastic excitations lie inside the same envelope (:211-236).
  - The isolated angular end-jacket sign obstruction recurs: left cut required −0.30436 against the admissible range [0.57369, 0.94360], and right cut Y(0)≥725.57 and ≤4.84 (JOINT_SUPPORT_REFINEMENT_AND_END_LOADS.md:127-137; the same pattern appears at GRADED:185-189 and VIRTUAL_RADIAL_CELL_CONSTRUCTION.md:342-352).
- **What detected it:** nodewise interval intersection through time, sign checks of dP·dℓ, and force-cone bounds. All are cheap analytic screens.
- **Available earlier:** yes. They were run within the same commits as the families they excluded. **This is a positive case of cheap checks catching problems early**, and the exact-certificate machinery made the exclusions final.
- **Cost:** low; the families were excluded quickly.
- **Candidate lesson:** when the demanded support stress changes sign or magnitude over the operating cycle (compression to tension), permanent, passive or conserved prestress cannot supply it. Test the temporal intersection of nodewise bounds before building a passive family.
- **Generality:** general to any time-dependent metric schedule. The specific force cones are design-specific.
- **Recurrence:** 4 (axial passivity, flux tubes, graded tubes, end jackets ×3).

---

## Counter-evidence (practices followed that did not help, or misled)

- **C1. An independent verification passed while incomplete.**
  - The joint-support audit was reported as passing an independent covariant-divergence test with nonzero shift (JOINT_SUPPORT_STRESS_SCHEDULE.md:211-213). The test's field energy was zero, so the omitted boost term was invisible (I10).
  - Independence of the code did not guarantee coverage of the terms. The audit itself was the erroneous component.
  - The correction then moved no decision (all changes ≤0.1 percentage point), so the erratum machinery cost more than its effect in this instance.
- **C2. Refinement ladders that converged without changing any decision.**
  - The elastic depletion time was refined four ways: 0.378546, 0.378636, 0.378630, 0.378391 (ELASTIC_ENDPOINT_STORAGE_INVESTIGATION.md:206-212). The event came from a forced one-way exchange on near-luminal material (I3), which refinement cannot reveal.
  - The EM stop-time convergence actively misled (I1).
  - The causal-conductor margin was certified over four resolutions: 0.00384673 → 0.00446190 (ACTIVE_RESERVOIR_CAUSAL_TRANSPORT.md:300-305). The branch was set aside anyway.
  - Graded peak-null refinement to 3.6% (GRADED:283-289) came before the coefficient-drop problem (I5).
- **C3. A relative figure of merit with no absolute acceptance threshold steered about 90 commits.**
  - Candidates were ranked by "required negative-null contribution": 75.78 → 5.28 → 0.104 → 0.2628 → 0.204 → 0.333 → 3.18.
  - The block explicitly "assigns no independent quantum capacity ceiling" (GRADED_ELECTROTHERMAL_ASSEMBLY.md:159-160) and proceeds "without assigning a numerical feasibility ceiling to quantum stress" (RESERVOIR_FEASIBILITY_ENVELOPE.md:108-109). Ten of the 26 reports defer the remainder to an unspecified negative-stress or quantum sector.
  - None cites the Sep 8 LE_* classification (0 grep hits). The ranking could not reveal that no remainder of any size was acceptable.
- **C4. Gate relaxations accumulated to reach a local pass.**
  - Phase E passes were obtained by successive relaxations, each labelled a "declared model test":
    - guide drift comparison 0.5 → 0.6 (infeasible) → 0.7 / 0.8 (pass) (PASSIVE_PHOTON_CLOSURE.md:549-583, 0.6 result at :569-571);
    - numerical reserve 0.2% → 0.5% (:618-621);
    - crediting the previously excluded pressure-link fluid and receiver inventories (`cc1c210`; PRESSURE_LINK_REALLOCATION.md:3-9, :26-37);
    - photon turnover required 23.42 against the declared 10 (:650-667).
  - The final pass is conditional on all of these, and the branch still stopped at the mass barrier (I6).
- **C5. Solver time limits and method choice consumed effort unrelated to physics.**
  - Many outcomes were "unresolved solver time limit" (THERMAL_EXCHANGE:244-249; PRESSURE_LINK_REALLOCATION:134-138, :365-367, :386-393; GRADED:227-229; STRESS_SCHEDULE:158-162).
  - Switching to HiGHS interior-point solved a timed-out case in 22 s (GRADED:233-236). Constraint generation resolved a time-limited program by checking 332,820 rows (CONSTRUCTION_REVIEW:130-134).
  - A HiGHS process-global thread-scheduler conflict needed a repair (`54685c4`; VIRTUAL_RADIAL_CELL_CONNECTION_AUDIT.md:418-421).
- **C6. Heavy provenance auditing caught no physics error, though it did enable clean recovery.**
  - Audits ran to 6,507 references over 79 manifests (PASSIVE_PHOTON_CLOSURE.md:683-693), plus 1,239 comparisons (CONSTRUCTION_REVIEW) and 825 (SCALAR). None flagged a modelling error in the block.
  - Their demonstrated value was operational: after the computer interruption (`3dbd12b`, `3759d2c`) "left the original replay directory empty" (PASSIVE_PHOTON_CLOSURE.md:637-639), three execution versions were recovered with exact SHA-256 matches (:689-693).
- **C7. The time-boxed session produced a large, conditional result.**
  - JOINT_SUPPORT_CONSTRUCTION_REVIEW records a "three-hour investigation authorized on 12 September 2026" (:11-16).
  - Within it, the selected target was reversed (I11), yet the session closed on a routed generic target with fade remainder 3.18 and null peak 1.77 against the comparison cap 0.2. This is a much more demanding target, not a closure.

## Cross-cutting lesson counts (this block)

| Lesson | Occurrences |
| --- | ---: |
| Enforce constraints between samples/nodes, not only at them (I11, I12) | about 7 |
| Screen stores by E/(Mc²) against the density budget first (I6) | 4 |
| Positive-energy supports raise the NEC remainder; screen k·T·k first (I4) | 4 |
| Complete-ledger comparison; partial ledgers flatter (I8, I9) | about 5 |
| Solver statuses are not physics; check original rows and certificates (I5) | 4 |
| Thermodynamic and passivity constraints belong inside the optimization (I13) | 4–5 |
| Source-free controls before calling a stop physical (I1) | 3 |
| Cheap analytic screens (force cones, interval intersections) excluded families early (I15, positive) | 4+ |
