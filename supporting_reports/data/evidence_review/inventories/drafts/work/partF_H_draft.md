## Part F. Counter-evidence: practices followed that did not help, or misled

Each item names a practice the project followed and the record showing it
failed to prevent, or actively caused, a problem. None of this shows that
the practice is bad. It shows the limits of what it certifies.

| # | Practice | What happened | Source |
|---|---|---|---|
| F1 | Passing tests and "independent" verification | The legacy classifier passed its 4 focused tests (and the May audit's 58) while failing 15/19 analytic fixtures and flipping rest-energy signs. The joint-support audit was "independent" code, but its test set `flux_energy=zero`, so the omitted term was never exercised. Sixteen robustness checks certified a one-sided shooting artifact. | A1, C10, B6 |
| F2 | Machine-precision verification and provenance hashing | Examples: 504 eigensystems to 1e-16, 147,528 action matrices, 6,507 references over 79 manifests, 264 hashes. In the C1 phase, the RSET agreed to 2.3e-9 and 222 manifest hashes were verified, and a 574-comparison spectral screen decided nothing (D8). None of these tested the premises that later failed: static surrogate, two-ended topology, magnitude, species bound. Their demonstrated value was operational, the recovery after an interruption (`3dbd12b`/`3759d2c`). | block notes; C-list |
| F3 | Refinement ladders | Many converged without changing any decision (semiclassical 5.01e-6 → 5.38e-6 against a 2×10⁵ gap; elastic depletion time refined four ways). The EM stop time converged although the stop was numerical. Node-level "refinement-stable" Type I verdicts missed bands (E8). The refinement that mattered, the Type IV witness converged to 0.001%, was cheap. | B-, C-lists, E8 |
| F4 | Per-candidate pre-registration and stop rules | Each candidate stopped honestly and fast. About 16 families were opened in about 25 hours on 8–9 Sep, and 183 commits followed to 17 Sep. The written program-level rule in the handoff was bypassed (A8, F14). | A8 |
| F5 | Local scope qualifications | They were present in the reports ("applies to this proposed equilibrium attachment"), yet later recommendations exceeded them. The 9 Sep scope correction did not constrain 10–17 Sep. | B10 |
| F6 | Affirmative-writing and no-running-log rules | They erased the negative gate verdict from the only document being updated (A9). The PDF-with-every-edit rule produced 6 rebuilds for content removed the same day. | A9, B13 |
| F7 | A relative figure of merit without an absolute threshold | Ranking by "required negative-null remainder" (75.78 → 0.104 → 3.18) steered about 90 commits and could not reveal that no remainder is acceptable. | Part C header |
| F8 | Gate relaxations declared as model tests | Guide drift 0.5 → 0.6 → 0.8, reserve 0.2% → 0.5%, crediting excluded inventories: the local pass came, and the branch still stopped at the mass barrier. In C1 the passes rested on stacked relaxations: arbitrary DEC material, continuous N, a granted angular target, field-selective transparency, zero m/q, free hosts, lossless photon control and chosen R² couplings. No ledger records which relaxations a pass depends on. | block notes, C6 |
| F9 | "Reproduce the reference audits" as a success criterion | The constant-radius track reproduced beta075's 2.569/1.233 service ratios exactly (`CONSTANT_RADIUS_TRACK.md` l.242). That carried the kinematic mismatch and the missing exterior path forward. | E3, E4 |
| F10 | Append-only reports | Superseded headlines stay at the top of reports (for example `SCREENED_SCALAR_CONDENSATE.md` l.3). The disclosure still says quantum fields supply the rail below 0.45 mm (E15). | B6, E15 |
| F11 | A single pass/fail gate as the design driver | Designs chosen to pass carried 450× excess energy, 9,069× clocks and a front horizon (γ = 10²²). | E7, E11, E13; P01 §2h–i |
| F12 | Reproducibility evidence and the parallel-worker rule | One batch committed about 238 MB of arrays. Two mid-research cleanups followed (1.282 GiB and 5.511 GiB; 2 commits, 2 reports). Four-worker parallelism was applied to jobs of 2.5 s and 10.3 s. | D-notes |
| F13 | "Preserve specialized components" with narrowly scoped exclusions | Exclusions were re-expressed as duties on components not yet built (D3 reopening; D10 reframing). Negative results did not accumulate, and the softening sat in leads and summaries (D5; the `57aadf8` lead rewrite). Report bodies carry 106 fail/reject/exclude mentions. | D3, D5, D10 |
| F14 | Written stopping rules | The handoff rule ("redesign before Comer inversion", 8 Sep) and the workflow rule ("insufficient normalized strength … ends", 17 Sep) were each bypassed on the day they applied. | A8 |
| F15 | A provisional topology preference | C1 was adopted before any C1 number existed. The first measurements (77% more support energy, twice the charge inventory) did not reopen it. The decision record requires evidence to change the preference but not to keep it. Weak item. | D-notes G |

## Part G. User corrections visible in the record

Source types:
- (R): stated in the repository.
- (I): inferred from the timing and wording of a reversal.
- (M): stated in the user's auto-memory files, which lie outside the repository.

| Date | Correction | Effect | Source |
|---|---|---|---|
| 9 Sep | Disclosure stripped of trial narratives. | The Le verdict was lost with them (A9). | `734156c` (I); the AGENTS.md rule was codified 16 Sep (R) |
| 9 Sep | "The previous recommendation … repeated work already established in the design record". | Archive re-screen. | `83fe023` (I/R) |
| 9 Sep | Scope correction: static background results are not rail selection gates. | Did not constrain 10–17 Sep. | `a1a8a65` (I/R) |
| 10 Sep | "the user's material-velocity concern" (γ ≈ 47). | Heat-supply chain redirected to the mechanics (C3). | `PRESTRESSED_BUFFER_VELOCITY_INVESTIGATION.md` l.237 (R) |
| 10 Sep | "The user has set this assembly aside"; string sources deferred. | Phase A closed (C4). | `RESERVOIR_FEASIBILITY_ENVELOPE.md` l.257–260 (R) |
| 12 Sep | "three-hour investigation authorized on 12 September". | Time-boxing. | `JOINT_SUPPORT_CONSTRUCTION_REVIEW.md` l.11–16 (R) |
| 16 Sep | The supplied gate handoff and Casimir handoff were committed as "separate research context", and `AGENTS.md` was created (report, disclosure and worker rules). | The handoff's decision rule was not wired into the plan (A8). | `e7a9951` (R) |
| 16 Sep | "Commit completed, validated milestones as work proceeds". | Followed the 33-second batch commit (D2). | `9083031` (R) |
| 17 Sep | "Numerical work is paused for discussion"; build topology C1 added to `AGENTS.md`. | Storage phase stopped (D6). | `ba93e0e` (R) |
| 17 Sep | "Preserve component roles": the radial-only exclusion was reframed. | D10. | `57aadf8` (I/R) |
| 17 Sep | Normalized-source workflow agreed; `AGENTS.md`: "Prioritize physically normalized component contributions". | The first normalized number changed a decision within 41 minutes (D8). | `1e9ac1d` (R) |
| 23 Sep | "Agreed direction": reinstate the gate, C∞ rule, redesign the geometry. | Redesign began. | `9be57e0`, plan l.27–36 (R/I) |
| 23 Sep | "Track termination: one space (decided)". | Axial track and one-space revision. | `2a3f404` (R/I) |
| 23 Sep | "tube"/"wall" renamed "service region"/"transverse boundary layer". The user had read the old names as a physical pipe. | Terminology. | `5aa0b49` (R); memory `geometry-region-terminology` (M) |
| 24–25 Sep | A 55× packet clock is a failure for crewed transit; report aging, tides and acceleration. | Compartment pass (E13). | memory `rail-goal-is-crewed-transit` (M) |
| 25 Sep | The disclosure update had not been authorized. | Process rule (E16). | memory `disclosure-updates-need-explicit-go-ahead` (M) |
| 25 Sep | Front trapping is the known warp-drive problem the user had raised in an earlier paper. | Framing (E11). | memory `answer-user-comments-directly` (M) |
| 25 Sep | Choreography may use planned timing and local fallback, never superluminal coordination signals. | Choreography columns in E11. | memory `rail-choreography-causality` (M) |
| 25 Sep | Investigate both branches of every fork. | Shelf recorded beside the cone. | memory `record-design-forks` (M) |
