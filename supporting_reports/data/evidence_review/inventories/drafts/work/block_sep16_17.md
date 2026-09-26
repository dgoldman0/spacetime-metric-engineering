# Incident inventory: block 2026-09-16 / 2026-09-17

Repo: `/media/projectspace/active-rail-refined-design-base` (read-only). Paths below are relative to it; `SR/` = `supporting_reports/`.
Line numbers are from the current working tree unless a `git show <hash>:<path>` form is given.

## Block shape (for cost estimates)

- 50 commits dated Sep 16–17; 41 new reports; ~473k inserted lines (`git diff --shortstat e7a9951~1 42e6688`).
- Phase S (storage / containment / optical / thermal / electrical / microscopic hosts): `e7a9951..4c576e0` = 39 commits (2 of them disk-cleanup), 31 new reports, ~182.7k lines. Sep 16 18:18 → Sep 17 09:36.
  - Opens with a batch: `e7a9951` + six technical commits (`702caec 1a4d9d4 cc4c300 96aa74c 86c6163 ebb606b`) all stamped 18:18:07–18:18:40. Those six add ~52.7k lines and ~238 MB of `.npz` arrays.
- Pause, then topology decision `ba93e0e` (Sep 17 09:44).
- Phase C1 (finite-module source screens on the static phase-0.745 surrogate): `4c576e0..42e6688` = 10 commits, 9 new reports, ~289.6k lines, Sep 17 12:27 → 19:49. User-directed workflow commit `1e9ac1d` falls in the middle (14:29).
- There are no commits Sep 18–22. On Sep 23, `9be57e0` (11:50) reinstates the Le gate and `9c1021a` (14:07) passes it with a redesigned C∞ constant-radius track. The redesign took about 2 h 17 min.

---

## Incidents

### I1. The Le gate went into the repo as "context", and the Sep 17 workflow had no gate stage
- **Date / commits:** `e7a9951` (Sep 16 18:18), `1e9ac1d` (Sep 17 14:29). Remedied in `9be57e0` (Sep 23).
- **What happened:** `e7a9951` committed `active_rail_test1_le_boundary_gate_handoff.md`, eight days after the Sep 8 LE work used it. The commit message files it as "separate research context". The handoff has a binding decision rule: "INTERNAL CLOSURE FAILURE — redesign before Comer inversion" (handoff:156) and "Only a PASS makes the Comer-style inverse constitutive tests the next priority" (handoff:162). The Sep 8 verdict was exactly that failure: "**Verdict: INTERNAL CLOSURE FAILURE for the geometry-demand gate** … refinement-stable Type IV layer" (`SR/LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:5-8`).
  - The Sep 17 workflow's investigation-order table goes straight from "Transport target" to "Physical source contribution" (`git show 1e9ac1d:SR/SOURCE_FEASIBILITY_WORKFLOW.md` lines 18-26).
  - The Sep 23 revision inserts a "Standing geometry gate" section and a "Geometry gate" row (current `SR/SOURCE_FEASIBILITY_WORKFLOW.md:18-31, 38`). It also adds: "A source allocation obtained on a static surrogate becomes a construction input after the same allocation is evaluated on the gate-passing active geometry."
  - The finer point: the handoff defines the static case as the *control*. Its step 4 is "Run a matched holding/static control" (handoff:119-126), and "edge is Type I in holding but becomes Type IV only during active current → Le-like flux/tilt failure" (handoff:126). Every C1 screen in the block uses the static, zero-shift phase-0.745 surrogate as its *design* geometry: `SR/C1_FINITE_MODULE_PAIR_SCREEN.md:25-29`, `SR/C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:46-48`, `SR/C1_ANGULAR_SCALAR_INVESTIGATION.md:36`, `SR/C1_ANGULAR_NORMALIZATION_AND_BOUNDARY_RESPONSE.md:37`, `SR/C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:29`, `SR/C1_JOINT_SOURCE_MESH_SCREEN.md:20-25`, `SR/C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:22`. That makes 7 reports, 7 commits.
- **Detected by:** the user and agent on Sep 23 ("Reinstate the Le boundary classification as the standing geometry gate"). `plan.md:298-301` says the static slice "leaves the current-driven Type IV demand untested".
- **Tool available when?** Since Sep 8, in the repo's own classifier and verdict.
- **Counterfactual:** once the gate was reinstated, a gate-passing geometry took about 2 h 17 min (`9be57e0` 11:50 → `9c1021a` 14:07 on Sep 23). Wiring the gate into the Sep 17 workflow table would have cost one table row and, by that later measurement, about two hours of redesign.
- **Cost:** the C1 phase (10 commits, 9 reports, ~290k lines). Arguably the whole block (50 commits) ran on beta075-derived histories or the surrogate.
- **Lesson:** a failed admissibility gate on the demanded tensor has to be a blocking step in the research-order document. A gate stored as "context" does not gate anything. When you evaluate on a surrogate, check that it is not the gate's own control case.
- **Generality:** general process lesson for any metric-engineering program with a classification gate. It is close to a truism, but the "control used as design case" twist is specific and instructive.
- **Recurrence in block:** 7 reports re-declare the surrogate as "Unchanged".

### I2. Batch commit of uncommitted work, then a user rule on commit discipline
- **Date / commits:** `e7a9951`, `702caec`, `1a4d9d4`, `cc4c300`, `96aa74c`, `86c6163`, `ebb606b` (Sep 16 18:18:07–18:18:40). Rule added in `9083031` (18:32:46).
- **What happened:** seven commits landed within 33 s. The six technical ones carry six reports, ~52.7k lines and ~238 MB of `.npz` state arrays; the largest single array is 51.8 MB (`magnetic_geometry/first_n32_t4113_states.npz`, `git show 1a4d9d4 --stat`). The LE handoff, used on Sep 8, was first committed here. Fourteen minutes later `AGENTS.md` gained: "Commit completed, validated milestones as work proceeds. Keep implementation, supporting reports, and reproducibility evidence in coherent commits." (`git log -p -- AGENTS.md`, `9083031`).
- **Detected by:** the user. This is the first of three user-directed `AGENTS.md` changes in the block, alongside `ba93e0e` and `1e9ac1d`.
- **Tool available when?** Always.
- **Counterfactual / cost:** the cost was provenance, not physics. In this batch the wall-rejection report and the ensemble report that reopens it (I3) land in the same second, so the history cannot show the order of the correction.
- **Lesson:** keep a commit per decision-bearing result, so that reversals and their triggers can be audited.
- **Generality:** process truism.
- **Recurrence:** 1.

### I3. Direction-averaged stress basis over-scoped a rejection; the "ensemble correction" reopened it; the finite construction failed again
- **Date / commits:** `96aa74c` → `86c6163` → `ebb606b` (Sep 16).
- **What happened:**
  - The current-carrying scalar wall, given the remaining sleeve load, "fails the required stress allocation at both saved locations" (`SR/CURRENT_CARRYING_WALL_MATERIAL_TEST.md:5-14`).
  - The ensemble audit then states: "This result reopens the existing component approach. The earlier scalar-wall test correctly rejects its specified wall duties…" (`SR/CONTAINMENT_ENSEMBLE_ROLE_AUDIT.md:13-18`).
  - Cause: "The loss of local directional information was consequential. In the original averaged support basis, a transverse Maxwell field and opposed axial photons both have tensor (u,p_z,p_⊥)=(1,1,0)… Their hoop and normal stresses differ" (`:38-42`).
  - With constituents resolved by direction, every sample passes. Minimum reserves are 0.00471315 (first fine) and 0.0140901 (second fine) (`:125-133`). The necessary strength bound drops to k ≥ 0.0217 and 0.0890 (`:154-172`), from the single-sleeve 0.7767 / 0.9746 (`SR/MAGNETIC_LOAD_BALANCING_TEST.md:5-12`) and 0.8065 / 0.6542 (`SR/MAGNETIC_GEOMETRY_COMPARISON.md:5-10`).
  - The reopening lasted one commit. `ebb606b` builds the finite coaxial version. "A fixed ensemble of ideal sheets, strings and pressure-control photons exceeds the available energy along both histories, including a sensitivity that grants every current host for free" (`SR/FINITE_CONTAINMENT_HOSTS_AND_EVOLUTION.md:5-12`). Extra allowance of 0.097–0.171 per label is needed; 32/32 labels are rejected (`:240-247`). The current-host bound rejects 10 first-fine samples (`:145-152`).
  - `SR/RAIL_STORAGE_AND_INTERFACE_STATUS.md:41` later calls this "the ensemble correction".
- **Detected by:** re-examining constituent roles, which fits the project's "preserve specialized components" stance. The batch commit hides whether the user prompted it.
- **Tool available when?** Principal-direction stress bookkeeping is elementary continuum mechanics.
- **Counterfactual:** carrying (p_z, p_θ, p_n) per constituent from the first sleeve screen would have avoided both the over-scoped rejection and the reopening round.
- **Cost:** about 3 commits and 3 reports of rejection → reopening → re-failure within one batch.
- **Lesson:** do not assign mechanical duties, or reject a material class, using stress tensors averaged over directions. Two sources with identical averaged tensors can carry different loads.
- **Generality:** general for anisotropic source engineering (shells, walls, strings). It is not specific to this design.
- **Recurrence:** the same pattern (a rejection re-scoped to "one assignment within a multicomponent role") recurs in I10 (`57aadf8`). Count 2.

### I4. A virial (von Laue / Bousso) bound predicted the O(1) containment-strength requirement before six commits measured it
- **Date / commits:** `702caec 1a4d9d4 cc4c300 96aa74c 86c6163 ebb606b` (Sep 16).
- **What happened:**
  - The cold bank must absorb heat at specific-energy increments of 7.136–9.348 c² (first location) and 3.084–6.256 c² (second) per unit of added rest inventory (`SR/STORAGE_CONTAINMENT_LITERATURE_REVIEW.md:17-25`).
  - The magnetic program then measured the required stress-to-total-energy ratio k: 0.7767 / 0.9746 (loop), 0.81147 / 0.99520 (original), 0.80655 / 0.65421 (best jacket). "Every tested geometry fails the whole-history comparison at k=0.5" (`SR/MAGNETIC_GEOMETRY_COMPARISON.md:133-146`). The energy-only bound is k ≥ 0.03227 / 0.13320 (`:19-22`).
  - Demonstrated materials fall far short. Nuclear-pasta modulus / rest energy is about 1.3e-5 (`SR/MAGNETIC_CONTAINMENT_MATERIAL_SEARCH.md:120-128`). REBCO/SPARC structural stress is about 1 GPa (`:104-118`). Textbook: Kevlar-class σ/(ρc²) ≈ 3e-11.
  - The program fell back to ideal k = 1 primitives (Nambu–Goto-type sheets and strings, oriented Maxwell fields; `SR/CONTAINMENT_ENSEMBLE_ROLE_AUDIT.md:44-62`).
- **Detected by:** numerical screens. The literature review itself contained the bound: Ciceron et al.'s virial analysis (`SR/STORAGE_CONTAINMENT_LITERATURE_REVIEW.md:41-45`) and Bousso's wall bound, E_wall ≥ E_γ/2 (`:70-86`).
- **Tool available when?** Von Laue's theorem (a static closed system has ∫T^{ij}dV = 0), the magnetic virial theorem and Bousso (2003). All were decades or years old, and all were cited on Sep 16.
- **Counterfactual:** one line. A reservoir holding energy that is order c² per unit of its own rest mass, inside a budget where the container's energy is counted, needs a container with stress/energy ~ O(1). Every demonstrated material is ≥ 1e4–1e10 short. The same one line would have skipped the geometry and material sweeps.
- **Cost:** 6 commits, 6 reports, ~52.7k lines, ~238 MB of arrays. Downstream, the storage chain continued on ideal primitives for ~30 more commits.
- **Lesson:** in spacetime engineering, any stored energy that is gravitationally significant within the source budget needs containment stresses comparable to energy density. Run the virial/DEC bound before any hardware geometry sweep.
- **Generality:** general and essentially textbook. It applies to any warp, wormhole or rail design that stores energy inside its own tensor budget.
- **Recurrence:** the k ≈ O(1) requirement reappears in 4 reports (load balancing, geometry, material search, current-carrying wall).

### I5. A standing necessary-condition rejection was carried through eight downstream reports, then left out of the status summary
- **Date / commits:** origin `ebb606b` (Sep 16). Carried in `9083031/3dd210f`, `151c5bb`, `5be82e8`, `595a84f`, `010420c`, `4cbc8f1`, `149c929`. Summary `4c576e0` (Sep 17).
- **What happened:**
  - The all-speed Cauchy–Schwarz host bound rejects 10 of 4,113×32 first-fine samples (4 of 2,057×16 coarse). The necessary coefficient ceiling is 1.31305e-8, against a retained 2.54415e-8 (`SR/FINITE_CONTAINMENT_HOSTS_AND_EVOLUTION.md:141-157`).
  - The same "ten rejected samples" caveat is repeated in `SR/MATERIAL_RECONFIGURATION_TEST.md:243-244`, `SR/DISTRIBUTED_RECONFIGURATION_AND_JOINT_BUDGET.md:243-245`, `SR/CONSTITUTIVE_JOINTS_AND_OPTICAL_REACTIONS.md:307-308`, `SR/CONTROLLED_OPTICAL_TRANSFER.md:272`, `SR/OPTICAL_STORE_SPLITTER_ROUTING_AND_LOSSES.md:356`, `SR/RAIL_INFRASTRUCTURE_TRANSFER_AND_REACTIONS.md:37` and `SR/STANDING_FIELD_HOLDING_AND_SOURCE_REQUIREMENTS.md:182-184`. Meanwhile optical controllers, loss budgets (1.273 ppm / 18.300 ppm) and joints were optimized downstream.
  - The status report at the requested pause leads with "Its strongest system result is a conditional holding and transfer budget across both locations" (`SR/RAIL_STORAGE_AND_INTERFACE_STATUS.md:5-11`). It does not mention the ten-sample rejection; it only lists "current binding" as an open requirement (`:34`).
- **Detected by:** the necessary bound itself (early). It never changed the decision.
- **Counterfactual:** treating the failed necessary bound as blocking would have stopped downstream optimization of this branch after `ebb606b`.
- **Cost:** about 8 reports of optimization built on a component with a standing rejection.
- **Lesson:** a failed necessary condition on a component should block optimization that depends on it, and must stay in every summary until resolved.
- **Generality:** general research-management lesson.
- **Recurrence:** 8 reports.

### I6. Implementation-first detour: a user-requested pause, topology recognition and workflow reset
- **Date / commits:** Phase S (`702caec … 4c576e0`). Pause and topology in `ba93e0e` (Sep 17 09:44). Workflow in `1e9ac1d` (14:29).
- **What happened:**
  - For 39 commits the program optimized rail hardware: magnetic jackets, elastic joints, optical guides with 0.62 ppm absorption, splitters, rotor stores, capacitor work ports, thermal relays, coax leads and fermionic-vortex rotor hosts. All of it assumed an implicit continuous backbone: "radial backbone, angular jacket… eighteen exchange nodes… complementary rail port" (`SR/RAIL_INFRASTRUCTURE_TRANSFER_AND_REACTIONS.md:26-47`).
  - `plan.md` at `ba93e0e` says "Numerical work is paused for discussion". The commit message for `4c576e0` records "the requested pause".
  - The topology decision says the continuous "snake-like build is one possible realization. Its route-length mechanical connection remains a construction choice requiring its own justification" (`SR/RAIL_BUILD_TOPOLOGY_DECISION.md:20-24`). It also says the storage results "add … an architectural preference without adding a physical feasibility result" (`:109-114`).
  - The first C1 screen then states: "The result supports doing finite-module design before refining the earlier local fixtures. Placement, source overlap and the extent of each internal load path materially change those fixtures' duties" (`SR/C1_FINITE_MODULE_PAIR_SCREEN.md:13-16`). Its energies "have a different measure from the earlier local storage ledgers" (`:107-109`).
  - The workflow sets the order: "Detailed rotor, fixture, routing and loss optimization resumes when its input requirements are supported by the combined source and operating construction" (`git show 1e9ac1d:SR/SOURCE_FEASIBILITY_WORKFLOW.md` lines 94-96, and 6-9).
- **Detected by:** the user (pause and topology discussion), then confirmed by the C1 placement screen.
- **Tool available when?** Sep 10. `SR/SOURCE_CONSTRUCTION_SELECTION.md:9-11` already prioritized "assemblies with an independently supplied complete source". Systems-engineering order (requirements before detailed design) is generic knowledge.
- **Counterfactual:** a single finite-pair placement screen (`378a4b9` ran 68 cases in four workers) run on Sep 16 would have shown that fixture duties depend on placement.
- **Cost:** 37 technical commits, 29 technical reports, ~180k lines, about 15 h of commit time. They remain as "conditional inputs" (`SR/C1_FINITE_MODULE_PAIR_SCREEN.md:193-194`) and are not reused.
- **Lesson:** do not optimize subsystem hardware until the source mechanism and topology that fix its duties are settled. Otherwise the duties change underneath the optimization.
- **Generality:** a general engineering truism. The spacetime-specific part is that source placement and overlap in GR change local duties non-additively (`SR/RAIL_BUILD_TOPOLOGY_DECISION.md:94-99`).
- **Recurrence:** the downstream-first theme recurs in C1 reports that each repeat "detailed fixture … follows the combined source balance" (`SR/C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:273-275`, `SR/C1_ANGULAR_NORMALIZATION_AND_BOUNDARY_RESPONSE.md:285-286`, `SR/C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:334-335`). Count 4.

### I7. Physical normalization arrived last, and it exposes mutually incompatible scales across source families (the Planck-scale question)
- **Date / commits:** `4c576e0` (normalization section, Sep 17 09:36). Scale facts date from Sep 9 (`e3c17ae`, `868b938`) and Sep 12 (`5e59da3`). Acknowledged Sep 23 (`plan.md:302-305`, `9be57e0`) and quantified Sep 25 (`d128547`).
- **What happened:**
  1. **The scale was inherited, never chosen.** η = 2.41279e-5 is an *eigenparameter* of the Sep 9 condensate matching problem: "Two eigenparameters determine the positive gravitational conversion g=Gv² …" (`SR/CONDENSATE_JOINT_CONTINUATION.md:13, 60`). The C1 quantum screens reuse it as "the inherited gravitational conversion" (`SR/C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:89-90`; `SR/C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:52-54`). That same condensate branch had already failed its source test. It was "roughly 186,000–204,000 times too small" (`SR/CONDENSATE_SUPPLIED_QUANTUM_STRESS.md:7`), and the semiclassical opening supplies about 5.0e-6 of the required balance (`SR/SEMICLASSICAL_JOINT_INVESTIGATION.md:102`, Sep 9).
  2. **The Planck scale was on record by Sep 9:** "R_0/√η = 415.22" Planck lengths (`SR/LONGITUDINAL_QUANTUM_SOURCE_LITERATURE.md:229-232`). One rail unit is 204 ℓ_P ≈ 3.3e-33 m (`SR/DEMAND_CENSUS.md:211-212`, Sep 23). No Sep 16–17 report states this scale.
  3. **The storage ledgers ran in "inherited ledger units" until the pause.** The normalization C_J/δ_s = (c⁵/G)(Ĉ/δ̂)ΔxΔΩ and C_Jδ_s/ħ = (L_g/ℓ_P)²ĈδΔxΔΩ first appears at `SR/RAIL_STORAGE_AND_INTERFACE_STATUS.md:99-135` and `SR/FINITE_ELECTRICAL_LEADS_AND_CURRENT_HOSTS.md:138-172`. The commit message says "Correct the physical cell normalization". A draft had applied the volume factor D twice ("applying another factor of D would duplicate the volume weighting", `SR/RAIL_STORAGE_AND_INTERFACE_STATUS.md:101-105`).
     - Anchoring the electrical host to protons needs C_J/δ_s = 9.34732e21 W and a cell measure ΔxΔΩ = 1.74e-34 (first) or 4.99e-34 (second) (`SR/FINITE_ELECTRICAL_LEADS_AND_CURRENT_HOSTS.md:164-169`).
     - The rotor-host layout needs a common energy-time unit ≥ 9.18775e32 ħ (`SR/FINITE_RADIUS_CARRIER_REQUIREMENTS.md:122-127`).
     - Carrier m/|q| = 2.54415e-8 was set "without a particle species or a complete SI conversion" (`SR/MAGNETIC_CONTAINMENT_MATERIAL_SEARCH.md:113-118`).
  4. **The scale markers conflict.**
     - The Maxwell field supplies 95% of throat tension in every C1 screen (`SR/C1_FINITE_MODULE_PAIR_SCREEN.md:31-35`). The Sep 12 record already gave the pair-production scale: "L about 4.43e8 m places the peak near the electron Schwinger field" (`SR/CHARGED_CAPACITOR_CONSTRUCTION.md:266-271`).
     - *Derived check (mine):* the throat field is E ≈ √(2·0.95·0.009565·c⁴/(G L² ε₀)) ≈ 5.0e26 V·m / L. That means L ≳ 3.8e8 m to stay below 1.32e18 V/m. At L = 204 ℓ_P, E ≈ 1.5e59 V/m, about 1e41 × Schwinger.
     - Quantum fields can source the demand only for L ≲ 0.45 mm (species bound, `SR/SOURCE_SCALING_TEST.md:15-24`, Sep 25).
     - *Derived (mine):* the rotor host's 9.19e32 ħ versus (L/ℓ_P)² ≈ 4.1e4 at η, times ΔxΔΩ ≤ ~200 for the whole rail, falls short by ~1e26. It needs L ≳ 1e15 ℓ_P.
     - Crewed transit (the project goal) needs L ≳ 1 m.
     - No single L satisfies the C1 source mix. `plan.md:302-305` (Sep 23) records: "The physical scale targeted by the project is an open decision."
- **Detected by:** partly at the pause (`4c576e0`). Fully only on Sep 23–25 (DEMAND_CENSUS, SOURCE_SCALING_TEST).
- **Tools available when?** (ℓ_P/L)² scaling of quantum stress is textbook: Ford–Roman quantum inequalities (1995–96), and Pfenning–Ford (1997) find warp-bubble walls of order 100 ℓ_P. The Schwinger field dates from 1951. All three in-repo scale markers existed by Sep 12.
- **Counterfactual:** yes. A one-page scale table written on Sep 9–12, listing η → 415 ℓ_P, the Schwinger L ≳ 4e8 m and the crewed L ≳ 1 m, would have shown before the block that the Maxwell + semiclassical-quantum source mix cannot coexist at any size. It would also have shown that macroscopic hardware analogs (REBCO, SMES, ppm optics, coax leads) have no meaning at 3e-33 m. This would plausibly have redirected both phases: first choose L, then choose source families that scale correctly at that L. The Sep 25 source-scaling test is essentially that table.
- **Cost:** both phases. 48 technical commits carry microscopic parameters with no physical scale, or at a scale incompatible with their companions.
- **Lesson:** fix the physical scale (or an admissible scale window) before choosing source families. Each family carries its own power of ℓ_P/L (classical fields: pair-production and material limits; quantum fields: (ℓ_P/L)² relative to demand; species bound). A scale inherited from a solver eigenparameter is not a design choice.
- **Generality:** fully general to spacetime engineering. The Planck-thin wall result for warp drives is textbook. The "scale inherited from an abandoned branch" aspect is specific but instructive.
- **Recurrence:** 4 distinct unanchored microscopic parameters in Phase S (m/q, χ_host, 0.62 ppm, rotor action). η is inherited in 5 C1 reports.

### I8. Workflow correction `1e9ac1d`: normalize before validating structure. The first normalized number changed a decision within 41 minutes
- **Date / commits:** `a9217d5` (13:59) → `1e9ac1d` (14:29) → `a955302` (15:10).
- **What `1e9ac1d` corrected:**
  - The workflow (user-agreed: "Direction agreed after the source-first review and the C1 angular-scalar spectral investigation", lines 3-4) separates claim scopes: "An algebraic allocation identifies a target. A positive mode spectrum supports state construction. A supplied source contribution addresses the required stress" (lines 76-79). It requires "Normalized tensors or decisive bounds, fixed physical parameters" (line 23) and "Microscopic information enters as early as its consequences require. Mode count … can determine the sign or scale of a source" (lines 28-30).
  - Before it, the angular source had been "granted" as a target (`SR/C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:174-177`). Mode counts had been "continuous nonnegative values as a favorable mode inventory relaxation" (`:195-197`). The spectral screen ran 574 comparisons plus 44 independent spectra, yet "this field's spectral condition alone selects neither compartment count nor overlap bracket" (`SR/C1_ANGULAR_SCALAR_INVESTIGATION.md:7-12, 117-122`).
  - In short, the correction targeted un-normalized or granted source terms counted as progress. The earlier storage reserves were dimensionless-consistent (homothetic), so they were not meaningless. But they were unanchored (I7), and they used "a different measure" from C1 (`SR/C1_FINITE_MODULE_PAIR_SCREEN.md:107-109`).
- **What the first normalized computation showed (`a955302`):**
  - One real field at ℓ=1 supplies angular-null stress −1.47160e-10 at the throat, against a remaining duty of −0.00857644. That needs 58,279,574 fields (ℓ=0.5: 174,838,720; ℓ=2: 24,976,960; ℓ=4: 11,655,915) (`SR/C1_ANGULAR_NORMALIZATION_AND_BOUNDARY_RESPONSE.md:127-153`).
  - Internal reflection adds 0.6% useful throat response going from 8 to 32 compartments (`:171-172`). Meanwhile the left-end force goes from 9.0300 (retained radial) to about 2,741 (8 compartments) and about 1,510,000 (32 compartments). The shared right module would carry about −74.2 million (`:213-225`).
  - Decision changed: "Further blanket angular reflection … requires a demonstrated combined benefit" and angular transparency is prioritized (`:276-281`; `SR/SOURCE_CONSTRUCTION_SELECTION.md:20-27`).
- **Detected by:** the user's workflow direction, followed by the normalized difference calculation.
- **Tool available when?** Butcher (2014) eq. 59 and η were in the repo on Sep 9 (`SR/SOURCE_CONSTRUCTION_RESTART_SHORTLIST.md:101-104`; `SR/LONGITUDINAL_QUANTUM_SOURCE_LITERATURE.md:222-227`). The throat remainder existed by `e968b01`.
- **Counterfactual:** N ≈ duty × 2880π²R⁴/(η·|angular coefficient|) is one line. It could have preceded both the 80-case channel LP and the 574-case spectral screen. The Casimir force scaling (∝ N/d⁴ per compartment) likewise predicts the reflection-load blow-up.
- **Cost:** 2 commits (`e968b01` partly, `a9217d5` entirely) of structure validation that did not bear on any decision.
- **Lesson:** establish the normalized magnitude of a candidate contribution before validating its structure (signs, spectra, algebraic fits). Structure checks cannot rescue a magnitude shortfall of 10⁷.
- **Generality:** general.
- **Recurrence:** "granted target / continuous multiplicity" appears in 3 C1 reports.

### I9. Multiplicity treated as a free continuous knob; the species bound (applied only on Sep 25) invalidates the semiclassical regime
- **Date / commits:** `a955302`, `247b988`, `3975f7b`, `42e6688` (Sep 17).
- **What happened:**
  - After normalization, N was kept as a continuous allocation variable: "Scalar copy counts and radial central charges are continuous allocation variables in this screen" (`SR/C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:230-233`).
  - Representative allocations use 24,976,154–24,976,426 left scalars (`SR/C1_JOINT_SOURCE_MESH_SCREEN.md:143-148`) and 24.97 million (`SR/C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:151-155`). Radial central-charge sums reach 283,517,387 (`SR/C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:205-210`) and 8.0898e8 (`SR/C1_JOINT_SOURCE_MESH_SCREEN.md:198-200`).
  - The workflow's own stopping rule lists "insufficient normalized strength" (`git show 1e9ac1d:…` lines 90-94). It was not invoked, because N absorbed the shortfall.
  - The same morning, species-counted loop corrections were computed for the rotor host: 140 Dirac species, loop coefficient 1.77312 × tree (`SR/NEUTRAL_FERMIONIC_HOSTS_AND_OCCUPATION.md:157-172`). No analogous check was made for 25–58 million angular scalars.
- **Derived check (mine), using the Sep 25 repo method:** ℓ_* ≈ √N ℓ_P (`SR/SOURCE_SCALING_TEST.md:144-166`, Dvali). For N = 58.28M, 24.98M and 11.66M, ℓ_* ≈ 7,634, 4,998 and 3,414 ℓ_P, which is 18×, 12× and 8× the 415 ℓ_P throat radius. The throat then lies inside the gravitational strong-coupling length of its own field content, where semiclassical gravity does not hold. (Central charge is not directly a species count for Landau-level channels, so this check applies firmly only to the 4D scalars.)
- **Detected by:** not in block. Sep 25's `d128547` concludes "A quantum-sourced rail thus operates at the gravitational cutoff of its own field content, whatever its size" (`SR/SOURCE_SCALING_TEST.md:163-167`).
- **Tool available when?** Dvali's species bound dates from 2007–2010. The count of real Standard Model fields (~10²) is also textbook.
- **Counterfactual:** a one-line check at `a955302` (15:10 Sep 17) would have ended the multiplicity route before `247b988`, `3975f7b` and `42e6688`.
- **Cost:** 3 commits and 3 reports; ~200k lines of data for population allocation.
- **Lesson:** a large-N semiclassical source must pass the species bound, ℓ_P√N below the smallest curvature radius. Multiplicity is not a free design knob.
- **Generality:** general to all semiclassical sourcing (wormholes, warp shells, Casimir-type rails). Textbook-grade.
- **Recurrence:** 4 reports use continuous N.

### I10. A state-independent anomaly identity excluded radial conformal channels; a user-directed reframing 14 minutes later turned the exclusion into a requirement on another component
- **Date / commits:** `e968b01` (13:17) → `57aadf8` (13:31).
- **What happened:**
  - (ρ_Q − p_{r,Q}) = ηc/(48π²R²)(a″ + a′²) is independent of state and cavity length (`SR/C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:126-131`).
  - At the transition, the geometry needs (ρ−p_r) ≈ −0.001004672 (−0.0010375 after Maxwell), while the channel coefficient is +0.000357601. So every nonnegative mix with DEC matter has the wrong sign (`:137-149`), and all 80 radial-only comparisons fail (`:13-18, 279-284`).
  - The original lead said: "Finite reflecting radial conformal channels fail the full standing tensor requirement … A local energy–pressure identity gives a stronger exclusion of this bulk source family." `57aadf8` rewrote it to lead with the "conditional radial-plus-angular allocation" and "limit the radial-only exclusion to its restricted comparison" (commit message; diff of `SR/C1_SIGNED_SOURCE_CHANNEL_SCREEN.md`). The exclusion became a lower bound on the angular target, v ≥ max[0, ((ρ_Q−p_{r,Q}) − (ρ−p_r)_after Maxwell)/4] (`:159-166`).
- **Detected by:** analytic subtraction during the screen. The reframing was user-directed ("Preserve component roles").
- **Tool available when?** Sep 9. The exact 2D components ρ₂, p₂ appear at `SR/LONGITUDINAL_QUANTUM_SOURCE_LITERATURE.md:155-162`, and ρ₂ − p₂ follows by subtraction. The 2D trace anomaly is textbook (Davies–Fulling–Unruh 1976; Christensen–Fulling 1977).
- **Counterfactual:** the sign obstruction was derivable on Sep 9, before any LP. The 80 comparisons, with 140 exclusion witnesses verified independently, took 10.3 s of compute (`:305`), so the compute cost was small. The cost was the day's framing.
- **Cost:** small in compute. The reframing kept a two-component construction alive, and it then needed 25–58 million angular fields (I8, I9).
- **Lesson:** anomaly-fixed combinations of stress components cannot be tuned by state, cavity length or multiplicity sign. Derive these sign constraints analytically before any allocation. Re-labelling an exclusion as "a requirement on another component" is legitimate only if that component is then normalized promptly.
- **Generality:** general for conformal and 1+1 channel sources. The identity is textbook.
- **Recurrence:** the identity is reused as an exclusion certificate at `SR/C1_JOINT_SOURCE_MESH_SCREEN.md:58-71` and `SR/C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:102-129` (F(D) = −0.0157109503 at x = 0.517851). Count 3.

### I11. Sparse-probe allocations reversed as probes were added; each fix moved the deficit to the new boundary it created (edge migration)
- **Date / commits:** `247b988` → `3975f7b` → `42e6688` (Sep 17 16:03–19:49).
- **What happened (sequence):**
  1. ℓ₀ = 4: "Both sampled points admit ordinary completion" at 2 probes (`SR/C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:264`). It "fails after the transition probes are included" at 4 probes (`SR/C1_JOINT_SOURCE_MESH_SCREEN.md:129-133`) and in all 6-probe models (`:187-191`).
  2. The frozen 4-probe witnesses fail at the nearby points x = 0.01 and 0.05 by up to 5.8e-6 (`:180-184`).
  3. Dense 2,049/8,193-point arrays show ρ−p_r ≈ −0.333 (4-probe) and −0.387 (6-probe) at the population-group boundary x ≈ 0.51785 (`:222-225`).
  4. "The existing six-coordinate allocations fail the expanded spatial checks", with ρ−p_r = −0.38632 (`SR/C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:85-89`). All 84 fixed-partition comparisons fail (`:93-100`).
  5. After inserting 6 radial walls (4 subdivisions) and an angular wall at 0.30, 16/72 cases pass at the 11 samples (`:140-149`). A 1,025/4,097-point check then finds (ρ+p_t) = −0.00796195 at x = 0.300001, the new angular endpoint (`:207-214`).
  - This is the pattern the Le handoff warned about: "does the composite source actually cure the edge, or merely move it outward one layer at a time?" (handoff:24, 103).
- **Detected by:** denser sampling and dense residual arrays.
- **Tool available when?** Dense residual checks were used in the same commit series. The handoff's edge-migration test has been in the repo since Sep 16 (Sep 8 in practice).
- **Counterfactual:** running the dense residual check first, before and after each placement change, would have exposed the moving deficit at `247b988`. That would have saved about 2 commits of probe-based allocation and flagged the migration pattern.
- **Cost:** 3 commits, 3 reports; 156 allocation audits plus 96 in the earlier set.
- **Lesson:** pointwise feasibility at sparse probes is not feasibility. Check continuous or dense coverage, especially at the boundaries an allocation itself introduces. Track where the worst residual goes after each fix.
- **Generality:** general to inverse source allocation in any metric-engineering design.
- **Recurrence:** 3 reversals within the block (ℓ₀=4; 4-probe → 6-probe; 6-coordinate → 9-coordinate → dense).

### I12. Feasibility hinged on an unfixed renormalization coupling
- **Date / commits:** `247b988` (Sep 17 16:03). Carried in `3975f7b` and `42e6688`.
- **What happened:**
  - With ℓ₀ = log(R₀/a₀) = 1, the overlap "fails for every nonnegative neighboring population". Only ℓ₀ = 2 and 4 pass the 2-probe test (`SR/C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:257-264`). The corresponding a₀ values are 1.2371, 0.7503, 0.2760 and 0.03736 (`:130-131`).
  - The report is explicit: "a change of subtraction convention is accompanied by a compensating change of α, β. The total balance is invariant … The favorable cases therefore require those physical couplings … A material mechanism for adjusting the couplings has yet to be established" (`:133-150`).
  - Subsequent work nevertheless proceeded with ℓ₀ = 2 as the representative case (`SR/C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:29-31, 79-83`). ℓ₀ = 4 later failed (I11).
- **Detected by:** the same report (early and correct).
- **Tool available when?** Wald's axioms: the renormalized stress tensor is fixed only up to the local conserved terms ⁽¹⁾H and ⁽²⁾H (Wald 1977/1994; Birrell–Davies §6). This is textbook.
- **Counterfactual:** declare early that the only covariant choice free of new physics is the one with ℓ₀ fixed by an independently measured R² coupling, and stop if feasibility requires tuning it.
- **Cost:** 2 commits continued on a parameter case whose physical basis was flagged as missing.
- **Lesson:** a semiclassical "source" whose feasibility depends on the finite part of R² couplings is not a source until those couplings are physically specified. Changing the renormalization label moves stress between the two sides of the equation; it does not create stress.
- **Generality:** general to semiclassical metric engineering.
- **Recurrence:** 3 reports carry the ℓ₀ dependence.

### I13. A finite-differentiability reference metric was used for fourth-derivative vacuum stress
- **Date / commits:** `247b988`, `3975f7b` (Sep 17). Resolved by the C∞ design rule on Sep 23 (`9c1021a`, `SR/CONSTANT_RADIUS_TRACK.md:122-137`).
- **What happened:**
  - The absolute RSET includes H_{μν} from the variation of (3R_{αβ}R^{αβ} − R²) (`SR/C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:61-69`), which contains fourth metric derivatives.
  - The reference metric has C² Hermite joins from the Sep 8 repair (`SR/LE_BOUNDED_METRIC_REPAIR.md:71-73`). The report samples "smooth portions" and states "A complete spatial source construction must specify the joins' higher-derivative or interface treatment before integrating a global absolute stress ledger" (`SR/C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:203-207`; also `SR/C1_JOINT_SOURCE_MESH_SCREEN.md:289-292`).
  - The repo already knew the consequence. On Sep 9 a curvature step produced a "positive d⁻² energy term … fails the regular semiclassical source equation" (`SR/CONDENSATE_SUPPLIED_QUANTUM_STRESS.md:5, 116`).
- **Detected by:** the report (flagged). It was acted on six days later.
- **Tool available when?** Hadamard/point-splitting regularity requirements are textbook, and the repo had its own Sep 9 result.
- **Counterfactual:** a C∞ remake took hours on Sep 23. Doing it before `247b988` would have made the global ledger possible.
- **Cost:** C1 absolute results are restricted to sampled smooth points; no global energy ledger was possible.
- **Lesson:** semiclassical source work needs metrics smooth to at least fourth order, in practice C∞. Piecewise C² repairs that suffice for classical classification invalidate RSET ledgers.
- **Generality:** general.
- **Recurrence:** 2 reports.

### I14 (minor). An unbounded LP concentrated support material; refinement caught it, and the relaxation was later dropped again
- **Date / commits:** `378a4b9`, `e968b01` (Sep 17).
- **What happened:**
  - "The initial relaxation allowed arbitrarily concentrated supports. Its maximum density grew under refinement, and one narrow outer-overlap case changed sharply" (`SR/C1_FINITE_MODULE_PAIR_SCREEN.md:88-91`). The fix was an envelope, ρ ≤ 4ρ_{E,0} = 0.0363466842, with the same bound on gradients (`:93-96`).
  - The next screen "relaxes the earlier optimized profiles and density/gradient envelopes" (`SR/C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:58`). Its passing allocations have peak densities 0.097987 and 0.086404, 2.4–2.7× the previous envelope (`:222-225`).
- **Detected by:** the grid-refinement ladder, early.
- **Lesson:** minimum-energy linear programs without regularity bounds converge to distributions (textbook LP / bang-bang behavior). Keep the regularity bound once found, or record every pass that violates it.
- **Generality:** general numerical-method lesson.
- **Recurrence:** 1 (and see counter-evidence D).

### I15 (minor). An illustrative cut drove the vortex coupling into a non-perturbative regime; it was replaced 33 minutes later
- **Date / commits:** `66beb98` (08:19) → `d4ade64` (08:52), Sep 17.
- **What happened:**
  - The illustrative cuts z = k_F/m_f ≤ 0.3 and ℓ_g ≤ 0.1 forced β = 5.83701e-11, g = 3.973835. The quartic loop/tree diagnostic there is 2.70539e10/e² (`SR/FERMIONIC_STRING_MATERIAL_CANDIDATE.md:103-107, 137-141`).
  - The finite-radius screen replaced the cut: β=1, g=1 gives 0.00633, but at R√μ = 11,803.4 (`SR/FINITE_RADIUS_CARRIER_REQUIREMENTS.md:3-9`). That radius then implies node action ≥ 9.19e32 ħ (see I7). The follow-up needed 70 pairs, i.e. 140 Dirac species, with loop coefficient 1.77312 × tree (`SR/NEUTRAL_FERMIONIC_HOSTS_AND_OCCUPATION.md:157-172`).
- **Detected by:** the report's own loop diagnostic. It was caught early.
- **Lesson:** when a parameter is tuned to an extreme value to meet an illustrative cut, check perturbative control (loop/tree) in the same step.
- **Generality:** general field-theory hygiene.
- **Recurrence:** 1.

---

## Counter-evidence (practices that did not help or that misled)

**A. Validation-heavy structure checks carried no decision content.**
- The angular spectral screen ran 574 comparisons, 44 independently recomputed spectra, 28 tests and 49 hashes, with a production run of 2.49 s. Its result: "spectral condition alone selects neither compartment count nor overlap bracket" (`SR/C1_ANGULAR_SCALAR_INVESTIGATION.md:117-122, 190-211`).
- The user's workflow immediately placed spectra in a lower claim scope (`1e9ac1d` lines 76-79).

**B. Exquisite numerics passed while the premise was invalid.**
- The absolute angular RSET has nine independent mode comparisons within 2.3e-9, a trace discrepancy of 1.9e-11 and throat components stable to 4.8e-14 (`SR/C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:172-187`). C1_POP verifies 222 manifest hashes (`SR/C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:257`).
- All of this is on a static surrogate of a gate-failing geometry (I1), with C² joins (I13), at a 415 ℓ_P throat inside its own species length (I9).
- Storage reports routinely reran two resolutions (n16/n32) that reproduced every verdict, for example "Both coarser histories reproduce the rejection" (`SR/CURRENT_CARRYING_WALL_MATERIAL_TEST.md:238-244`) and reserves of 0.00488856 vs 0.00471315 (`SR/CONTAINMENT_ENSEMBLE_ROLE_AUDIT.md:125-133`). Precision and independent verification did not catch errors of scope or scale.

**C. The reproducibility-evidence practice created disk pressure and two cleanup detours.**
- The batch alone committed ~238 MB of `.npz` arrays.
- Cleanup `dae3dfa` hard-linked 66 duplicate CSVs and released 1.282 GiB. Free space measured 2,183,737,344 B afterwards (`SR/REDUNDANT_RUN_STORAGE_CLEANUP_20260916.md:3-14`).
- Cleanup `4969f6b` rebuilt and hash-verified 337 CSVs (189.7 s, six workers) and removed 5.511 GiB (`SR/REBUILDABLE_RUN_CLEANUP_20260917.md:3-6, 21-23`).
- That is 2 commits and 2 reports spent on housekeeping in the middle of a research block.
- A related rule-following cost: four-worker parallelism was applied to jobs of 2.49 s and 10.3 s (`SR/C1_ANGULAR_SCALAR_INVESTIGATION.md:205`; `SR/C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:305`).

**D. "Necessary screens" with stacked favorable relaxations produced passes that constrain little.** The block's passes were granted, variously:
- arbitrary DEC aggregate material, dropping the earlier envelope (`SR/C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:58`);
- continuous channel counts (`:195-197`);
- the angular target granted outright (`:174`);
- field-selective reflector transparency (`SR/C1_ANGULAR_SCALAR_INVESTIGATION.md:41`; `SR/C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:34`);
- zero carrier mass-per-charge (`SR/C1_FINITE_MODULE_PAIR_SCREEN.md:101-103`);
- free current hosts, lossless photon control and free end fixtures (`SR/FINITE_CONTAINMENT_HOSTS_AND_EVOLUTION.md:141, 235-236`);
- favorable phase-field sharing (`SR/MAGNETIC_LOAD_BALANCING_TEST.md:9-11`);
- selected R² couplings (I12).

No ledger tracks which relaxations a given "pass" depends on. Each report is honest locally, but the passes do not accumulate into sufficiency.

**E. Role preservation and scoped exclusions made negative results non-cumulative.**
- The Sep 17 workflow says "Earlier exclusions retain the source laws and geometry families under which they were established" (`git show 1e9ac1d:…` lines 53-54), and a wrong sign "constrains the evaluated candidate and assumptions" (lines 90-91).
- Combined with "preserve specialized components" (`AGENTS.md`, `ba93e0e`), exclusions were re-expressed as duties on other, unbuilt components (I3, I10).
- Failures are well documented in report bodies (106 fail/reject/exclude/infeasible mentions across the 36 technical reports). The softening is concentrated in leads and summaries (`57aadf8` lead rewrite; `SR/RAIL_STORAGE_AND_INTERFACE_STATUS.md:7`).

**F. A written stopping rule was not applied the same day.**
- `1e9ac1d` lines 90-94 say "insufficient normalized strength … Repeated fitting or refinement ends when it leaves that cause unchanged."
- After `a955302` showed a 5.8e7 multiplicity requirement, three more commits (`247b988`, `3975f7b`, `42e6688`) refined population placement. The cause (per-field strength ~1e-10 against a duty ~1e-2) stayed unchanged.

**G. The provisional topology preference was shielded from measured costs.**
- C1 was adopted (`ba93e0e`) before any C1 number existed. The first measurement showed that mechanical separation costs 77% more support-material energy (2.48% of field + support), and the narrow pair carries twice the absolute charge inventory (28.188125 vs 14.094063) (`SR/C1_FINITE_MODULE_PAIR_SCREEN.md:143-158`). The record states "Both brackets therefore retain their previous architectural status" (`SR/C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:230-231`).
- The decision record requires a change of preference to "identify the … evidence that motivates it" (`SR/RAIL_BUILD_TOPOLOGY_DECISION.md:140-142`). There is no symmetric requirement for keeping it. The costs are modest here, so this is a weak item.

---

## Planck-scale normalization: direct answer

- **Could it have been computed earlier?** Yes, by Sep 9. η = 2.41279e-5 and R₀/√η = 415.22 ℓ_P were in `SR/LONGITUDINAL_QUANTUM_SOURCE_LITERATURE.md:229-232`. The about 5e-6 opening fraction was in `SR/SEMICLASSICAL_JOINT_INVESTIGATION.md:102`. The Schwinger scale L ≈ 4.43e8 m for the electric sources was in `SR/CHARGED_CAPACITOR_CONSTRUCTION.md:269-271` by Sep 12. The needed tools (ℓ_P/L scaling, Ford–Roman / Pfenning–Ford, Schwinger, Dvali species bound) are all textbook.
- **Would it have changed direction?** Very likely.
  - Phase S (magnetic/optical/electrical hardware with macroscopic analogs) has no physical meaning at 3.3e-33 m. Its microscopic parameters, once anchored, demand L ≳ 1e15 ℓ_P (rotor host; derived) or proton-benchmark cells of ΔxΔΩ ~ 1e-34.
  - Phase C1 combines a Maxwell throat field that needs L ≳ 4e8 m with quantum sources that need L ≲ 0.45 mm (Sep 25) and 25–58 million fields whose species length exceeds the throat.
  - Crewed transit needs L ≳ 1 m. That leaves no common window.
- **Nuance:** η was not chosen. It is an eigenparameter of the Sep 9 condensate matching (`SR/CONDENSATE_JOINT_CONTINUATION.md:13, 60`) inherited by later work. The project's scale was set implicitly by a solver from a branch that had already failed its own source test.

## Incident count summary
- 15 incidents: 13 substantive and 2 minor (I14, I15).
- 7 counter-evidence items (A–G).
- User-visible corrections in the record:
  - `9083031`: commit rule;
  - `ba93e0e`: pause and C1 topology;
  - `57aadf8`: preserve component roles;
  - `1e9ac1d`: normalized-source workflow;
  - later `9be57e0` (Sep 23): gate reinstated.
