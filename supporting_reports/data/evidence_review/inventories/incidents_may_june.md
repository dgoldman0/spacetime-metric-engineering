# Incident inventory: 16 May – 1 June 2026 (spherical-throat era)

Evidence gathering for the textbook vetting process. Nothing here is book text.
Repo: `/media/projectspace/active-rail-refined-design-base` (read-only; no
computations run). All paths are relative to the repo root unless absolute.
Line numbers refer to the files as they stand at HEAD unless a commit is named.

## Scope and conventions

- Period: the V10 freeze (legacy bundles imported 16 May, commit `60d6974`),
  the ADM harness (16–17 May), the V5 support shell (17 May), Stage I (17–19
  May), Stage II and beta075 (19–23 May), and the White Casimir side work
  (29 May – 1 June). Commits resume only on 8 September, so the "later
  detection" dates below are mostly 8–24 September.
- Commit volume, for cost estimates: about 190 physics commits from 16 to 23
  May, about 209 from 8 to 17 September (both on the throat geometry), and 28
  White Casimir commits from 29 May to 1 June. There are no commits between
  2 June and 7 September.
- Incidents already covered in `vetting/P01_classify_demand_before_sources.md`
  are not repeated. Section **P01+** adds May detail to them.
- **Evidence strength.** *Strong*: the record states the event, the numbers
  and the reversal or correction. *Moderate*: the facts are recorded, and the
  judgment that the event was an error is mine, supported by a later record.
  *Weak*: my inference only.
- **n** counts independent occurrences of the same lesson in the whole record
  (May–September), with each occurrence listed.

## Timeline of decision-changing events

| Date | Event | Incident |
|---|---|---|
| before 16 May (imported) | w_th cliff at 0.569 on 21×37 moves below 0.540 on 41×73; V10 freeze with last-safe V = 10.00 | I-07 |
| 17 May 08:22 → 08:55 | V5 support shell frozen at amplitude 1e-7; the 4D ledger shows the frozen amplitude does nothing | I-06 |
| 17 May | Stage I-B fails the passenger-separation test; Stage I-C fails at V10 | I-05, I-07 |
| 17 May | The disclosure cites the wormhole–warp correspondence as an analogy only | I-01 |
| 18 May | The target hierarchy is changed back to V5 as primary; V10 is demoted | I-07 |
| 18 May | The channel-cause ledger redirects knob tuning to the radial support law | I-15 |
| 19 May | The scalar kill screen stops the single-scalar search | I-20 |
| 19 May | SNEC failures at τ = 4 turn out to be boundary truncation; the larger domain exposes packet-norm failures at entry | I-13, I-04 |
| 19 May | A wiring bug is caught by a reproduction check | I-16 |
| 20 May | An entry gate reclassifies the failing points as "pre-entry setup" | I-04 |
| 20 May | The endpoint memo tests for a "literal transient wormhole throat" locally and rejects it | I-01, P01+ |
| 21 May | The "hard-affine" SNEC is found to use the lapse parameter; an affine audit follows | I-12 |
| 21 May | Dense bundles show caustic-like compression where central rays looked safe | I-14 |
| 21 May 15:25 → 21:11 | Packet-centreline probes never arrive; six hours later the service-time ledger reports a favourable advantage | I-02, I-03 |
| 22 May 21:26 | beta075 "seal" | I-10, I-11 |
| 23 May | The capstone claim is demoted the same day | I-17 |
| 23 May | V2.5 closure fails and V10 fails; the seal is rescoped to an operating point | I-11 |
| 23 May 18:51 | Finite-domain ANEC is negative on the demanded total; the residual is ablated | I-10 |
| 23 May | Quality review (`PROJECT_WORK_ANALYSIS.md`) | CE-1 |
| 29–30 May | White Casimir: morphology paper, then a magnitude ratio of 1e-39 | I-19 |
| 8 Sep | Complete-demand Type IV found | P01 |
| 23 Sep | The two readings of the packet's motion are found; the design moves to one space | I-01, I-02 |
| 24 Sep | Geometry clarification and addendum, six issues | I-01, I-02, I-03, I-17 |

---

## I-01 Unstated two-ended topology: the "rail" was a Morris–Thorne wormhole

- **Date, commit.** The geometry was present from the start. At `f0d709f` (17
  May) `adm_harness/source_ledger.py` l.154 sets
  `gamma_omega = (l*l + Rth*Rth) * c_omega**2`. That is the Ellis throat with
  minimal radius R_th = 1.75 at l = 0 and R → |l| on both sides. It was recognized on
  23 Sep (plan.md l.60–62, "Track termination: one space (decided)", commits
  `9c1021a`, `6e1a1fb`) and documented on 24 Sep (`db79203`, `86a557f`,
  `9bdf376`; `supporting_reports/THROAT_GEOMETRY_CLARIFICATION.md` l.42–83;
  addendum issues 1–2, `addenda/2026-09_Throat_Supported_Shift_Rail_Addendum.tex`
  l.57–63).
- **What happened.** The reduced metric uses spherical symmetry, with the rail
  coordinate l as the radial proper distance. Because R(l) has a positive
  minimum, the slices are R×S² with two asymptotic ends. The service
  "prepares" and "relaxes" the support stretch, the lapse and the angular
  jacket, while the minimal sphere persists through every service
  (THROAT_GEOMETRY_CLARIFICATION l.123–135). The paper and the disclosure
  described a rail between two endpoints, drawing on the Krasnikov-tube
  picture. Forming the geometry from ordinary space would need topology change
  (Geroch 1967), so the conditional feasibility claim had no path from
  ordinary space.
- **Missed opportunities in May.** Each used a tool that could have exposed
  the topology:
  1. 17 May `7147d94`: the disclosure adds a section on the
     Garattini–Zatrimaylov correspondence ("a Morris–Thorne wormhole metric can
     be written in a warp-drive-like form"). The correspondence is read as a
     "structural intersection" with the support-shell results, that is, as an
     analogy. It is never read as a statement about what the metric is.
  2. 20 May `fc6a03c`, `supporting_reports/STAGE2_ENDPOINT_THEORY_MEMO.md`
     l.57–70 (repeated in plan.md l.2604–2607): the memo tests whether the
     endpoint demand is a "literal transient traversable wormhole throat"
     using local R(l) statistics. It finds 0.07% of the deficit at areal-radius
     minima and 98.6% in d²R/dl² > 0 rows, and concludes "throat-like source
     demand, not yet literal … throat". Flare-out (d²R/dl² > 0) is the
     defining Morris–Thorne condition, yet it was read as evidence against a
     wormhole. The question was also local and "transient", while the throat
     is global and permanent.
  3. 21 May `cfe69bd`, `STAGE2_GZ_OBSTRUCTION_SCREEN.md` l.25–28: this screen
     computes an "areal-radius throat proxy" but tests only local tilt of the
     light cones.
  4. 23–24 May `45661a7`/`53c58b3`: the quiz bank cites topological
     censorship (Friedman–Schleich–Witt) and teaches that "local metric data
     does not by itself fix the complete global topology"
     (`toolkit/active_rail_quiz_system/src/data/questionBank.js` l.90–96,
     741–758). None of this was applied to the design.
  5. 23 Sep: the constant-radius track (`9c1021a`) is still two-ended, with
     flares at both ends (THROAT_GEOMETRY_CLARIFICATION l.59–62). The
     termination decision came the same day.
- **Detected by.** A design question about track termination, raised while
  building the constant-radius track, whose explicit flared ends made the two
  ends visible. The knowledge needed is textbook material: Morris–Thorne
  1988, Visser 1995 and Geroch 1967. The correspondence paper itself had been
  in hand since 17 May.
- **Counterfactual.** Catchable at zero compute cost on 16–17 May. Two checks
  would have done it: read R(l) as |l| → ∞ from the one code line, or note
  that a spherically symmetric slice whose travel direction is the radial
  proper distance, with R bounded away from zero, has two ends.
- **Cost.** All physics work in the repo before 23 Sep ran on a two-ended
  geometry: about 190 commits in May and about 209 in September. Beyond
  that work, the error affected the May paper's feasibility claim (addendum
  issues 2 and 6), the disclosure's throat metric (preserved at `2146526`),
  and the service-time ratios (I-03). A public addendum was needed.
- **Candidate lesson.** Establish and state the global structure of a metric
  ansatz before engineering it: its asymptotic regions, spatial topology, and
  whether it can be formed from ordinary space. A concrete, derivable trap:
  a spherically symmetric reduction that uses the travel direction as the
  radial proper distance and keeps R(l) > 0 describes a wormhole. A rail
  through one space needs a symmetry in which the track is not the radial
  coordinate of spheres. The redesign moved to axial symmetry for this reason
  (`AXIAL_TRACK.md`).
- **Generality.** High. Spherically symmetric proper-distance forms such as
  R² = l² + b² are common regularizations in the wormhole and warp
  literature, and topology change is established physics (Geroch).
  Topological censorship adds a second, independent consequence: a traversable
  two-ended geometry requires ANEC violation (see I-10).
- **Recurrence.** n = 1 root error with 5 missed checks, all listed above.
- **Verdict hint.** Established physics, plus an evidence-backed practice:
  state the global structure in the design specification. This is the
  strongest single incident in the period.
- **Evidence strength.** Strong.

## I-02 Two readings of the packet's motion

- **Date, commit.** Present from `f0d709f` (17 May). At that commit
  `source_ledger.py` l.135 defines the packet window as a bump in (l − s)²,
  l.339 defines the live mask as |l − s| ≤ R_pass, and l.147–149 compute
  `packet_norm = −α² + γ_ll (U_packet/B + β)²`. The window therefore moves at
  dl/ds = 1, while the norm uses the carry speed U/B. Found on 23 Sep
  (`5abcc98`, `RESET_SCHEDULE_OPTIONS.md` l.92–110) and fixed by the
  choreography pass (`cb3008a`, `CHOREOGRAPHY_PASS.md` l.4–6). This is
  addendum issue 4.
- **What happened.** Inside the compressed support B = 8, U/B is 0.625
  before the catch and 0.0625 after it. When the live window closes
  (σ = 1.645), the velocity reading places the packet at ℓ = 0.853 while the
  window centre sits at 1.645. The windows lead the packet by 0.8–0.9, more
  than twice the window radius of 0.35 (RESET_SCHEDULE_OPTIONS l.94–101).
  Every May "live packet" quantity was therefore sampled on a region the
  velocity-reading packet had left: packet-norm safety (on 260, 861 or 966
  live points), live fractions, live residuals and the entry gate (I-04). The
  packet norm itself evaluated the velocity field at points the packet did
  not occupy.
- **Signal in May.** 21 May 15:25, `1f17f11`,
  `STAGE2_SCHEDULED_ADM_PROBE_EVOLUTION_PILOT.md` l.75 and l.88: the
  `packet_centerline` probes follow the velocity field. All 24 end at the
  future boundary without arriving, which the pilot read as "scheduled-service
  completions, not radial escape failures". In September, 21 of 24 probes are
  still inside the track at σ = 15 (RESET_SCHEDULE_OPTIONS l.113–118).
- **Detected by.** Comparing delivery times across reset schedules, which
  forced the question of where the packet is.
- **Counterfactual.** Cheap. Integrating dl/dσ = U/B from the window start
  (a one-line ODE) and comparing it with l = σ would have exposed the gap.
  Both expressions sat in the same function from 17 May, and the 21 May probe
  result was a direct signal.
- **Cost.** No May packet-safety claim was ever verified on the actual
  worldline. The paper's packet screen and the service-time ledger inherited
  the mismatch (addendum l.71–78).
- **Candidate lesson.** The passenger worldline is a single curve, specified
  once as a prescribed path or an integrated flow line. Every passenger audit
  must evaluate on that curve: the timelike check, the exposure windows and
  the arrival time. Any moving window or bubble centre must follow the
  integral of the carry velocity. In Alcubierre's case, the shift at the
  centre must equal dx_s/dt.
- **Generality.** High. The lesson applies to any transport metric with a
  moving region and a carried observer.
- **Recurrence.** n = 1 root cause with 4 manifestations: the packet-norm
  screen, live-fraction accounting, the entry gate (I-04) and the service-time
  ledger (I-03).
- **Sub-note (moderate).** `packet_norm` was never normalized. It is g(u,u)
  in coordinate velocity, with values from −198.9 to −331,511 and up to
  +254,483 (`V_SWEEP_FINDINGS.md` table). Its magnitude was still read as a
  margin: "comfortably negative"
  (`STAGE2_BETA075_DENSE_ENDPOINT_SOURCE_STABILITY.md` l.87) and "max live
  packet norm −6.33" (`PROJECT_WORK_ANALYSIS.md` l.56, 385). September uses
  g(u,u)/α² (CHOREOGRAPHY_PASS l.22). The sign is valid, but magnitudes are
  not comparable across lapse profiles.
- **Evidence strength.** Strong for the mismatch; moderate for the sub-note.

## I-03 Service-time "advantage" built from the service factor and a light path the geometry lacks

- **Date, commit.** 21 May 21:11, `4920cdf`,
  `STAGE2_SERVICE_TIME_ADVANTAGE_LEDGER.md`. The rating entered the
  disclosure (`88fbd3f`, `c73f8d2`) and the paper. It was retracted on 24 Sep
  (addendum issue 5, l.74–78; THROAT_GEOMETRY_CLARIFICATION l.165–175).
- **What happened.** The ledger "reconstructs" the A-to-B distance in three
  ways (l.50–55): (1) `schedule_factor_distance`, the integral of U_packet
  (built from V); (2) the U_packet/B proxy; (3) the l = s centreline control.
  The resulting ratios were 2.568962, 1.233312 and exactly 1.0 (plan.md
  l.1747–1752). The only purely geometric measure was the neutral one, which
  the ledger dismissed as "the bookkeeping diagonal" (l.102). The result was
  recorded as "operational superluminal rating evidence" (l.114). Four days
  earlier, on 17 May (`436df5d`), V had been defined as "not the ordinary
  physical velocity of the passenger packet", with the schema still storing it
  as `service.velocity` (`ACTIVE_RAIL_VALIDATION_LADDER_RESULTS.md` l.7). The
  endpoints lie in separate asymptotic regions, so no exterior light path
  exists (I-01). Six hours earlier the packet-centreline probes had not
  arrived at all (I-02).
- **Propagation.** The ratios were still carried on 23 Sep: plan.md l.72–74
  says the one-space revision "keeps … both service-time advantages (2.569
  and 1.195)". The retraction came the following day.
- **Detected by.** The topology finding (I-01) plus the choreography pass,
  which shares one flat exterior between packet and light and gives a lead of
  1.66, a mean of 1.35c (CHOREOGRAPHY_PASS l.14–19).
- **Counterfactual.** The radial null tracers existed on 21 May
  (`74542a8`, the horizon escape ladder, the same day). A light ray from the
  departure event, compared with the packet worldline, needs no new tool.
  Once the topology was known, the comparison was undefined in any case.
- **Cost.** A headline claim of the disclosure and the paper, and one
  addendum issue.
- **Candidate lesson.** An arrival or speed claim compares two events: the
  packet's arrival and the arrival of a light signal sent from the same
  departure event through the same spacetime. A distance inferred from the
  transport parameter makes the claim circular. A parameter name that
  encodes a rejected meaning (`velocity` for a load factor) is a hazard.
- **Generality.** High. Every "effective superluminal" claim needs this. The
  literature has formal definitions of effective superluminal travel, for
  example Visser, Bassett & Liberati 2000 and Krasnikov 1998; both are **to
  verify** before citing.
- **Recurrence.** n = 1, with the related V-as-velocity conflation and I-02.
- **Evidence strength.** Strong.

## I-04 Entry gate: failing points reclassified as "pre-entry setup"

- **Date, commit.** 19 May `7b6b14c`, `STAGE2_HARD_AFFINE_SNEC_ADVERSARIAL.md`:
  the extended domain exposes the failures. 20 May 06:48 `5b8092a`
  (`STAGE1_COMPACT_ENTRY_STAGE_SCREEN.md`) adds the gate, and 07:55 `0a9b0df`
  accepts it (plan.md l.1700).
- **What happened.** The extended adjudication domain (101×151) exposed 2
  positive live packet-norm points at the early-entry edge, with a maximum of
  +1.6255 (STAGE1_COMPACT_ENTRY_STAGE_SCREEN l.5–9, l.66–69). The response
  added `live_packet_start` and classified every point with s < −1.40 as
  `pre_entry_setup`, outside live accounting (l.13–28). The positives
  disappeared. The Tkk peak (0.9393) and the pOmega peak (0.8880) were
  unchanged in the coarse screen (l.80–92), and the report states that live
  burden "drops because the newly exposed boundary cells are no longer
  charged to the passenger worldtube" (l.71–74). The geometry did not change.
  Where the packet was at those times could not be known in May (I-02). The
  memo calls this "The mild entry-stage redesign worked as intended"
  (`STAGE2_ENTRY_SERVICE_GATE_MEMO.md` l.3).
- **Detected by.** No later record explicitly re-adjudicates it. The
  September choreography pass prescribes entry at 0.9c on a defined path,
  which makes the question testable.
- **Counterfactual.** The failures were caught by domain extension, a good
  practice (I-13). The decision error came after detection.
- **Cost.** Small in compute. Its effect was on scope: the representative
  design's "clean live packet safety" rested on the reclassification.
- **Candidate lesson.** Changing what counts as passenger exposure is a
  design change to the service, namely when the passenger enters. It must be
  justified from the passenger's worldline, independently of where failures
  occur. A failure that vanishes under reclassification, with the geometry
  unchanged, has moved out of the accounting and remains in the geometry.
- **Generality.** Medium–high. The lesson applies to any zone-based or
  window-based safety accounting.
- **Recurrence.** "Reclassify or ablate to clear a failure": n = 4. The
  instances are this one; the Stage I-B metric substitution (I-05); the ANEC
  residual ablation (I-10); and the 22 May J regulator (P01).
- **Evidence strength.** Strong for the facts; moderate for the judgment,
  which is mine.

## I-05 The passenger-separation gate eroded and was replaced by a metric that cannot fail

- **Date, commit.** 17 May `3de5b48` through 21 May.
- **What happened.**
  - 17 May: the Stage I-B pass rule reads "max_live_packet_fraction_any_channel
    tiny, preferably below 1e-4 to 1e-3". The rules are "first-pass … can be
    adjusted after seeing the numbers" (plan.md l.3641–3649). The result was a
    fail, with 22% radial-null and 26% radial-pressure burden in the live
    packet (plan.md l.3038; `STAGE1_V5_MINIMAL_TRAVERSABILITY_SCREEN.md`
    l.121). Stage II was paused until the fractions fell "another order of
    magnitude or the project explicitly accepts a warning-grade Stage I
    target" (plan.md l.3056, 3197, 3242).
  - 18 May: the V2 memo sets the "strict band" at < 1e-2
    (`STAGE1_V2_LOW_SERVICE_GATE_MEMO.md` l.20). The design still fails at V2,
    and the memo says "Do not reframe … Stage II should remain paused"
    (l.93, 101).
  - 19 May: Stage II starts on the compact target (plan.md l.2630). The caveat
    recorded concerns the shell–throat residual. The live-fraction criterion
    disappears: "minimal traversability" last appears on 18 May, and no
    explicit acceptance of a warning-grade target is on record.
  - 20 May: `STAGE2_ENTRY_SECTOR_CLOSURE_DENSE.md` l.181 reads "The old Stage I
    `p_l` worry does not reappear … live `p_l` is assigned with zero live
    residual". Burden inside the passenger worldtube was assigned to named
    "live handoff" source components (C/E/F), so the residual is zero by
    construction (also `STAGE2_ENTRY_SERVICE_GATE_MEMO.md` l.7).
  - 21 May: full-grid live fractions are 2.889% radial-null, 0.787% radial
    pressure and 14.706% angular pressure (plan.md l.1757–1760). That fails
    both the 1e-3 and the 1e-2 thresholds, and the design went on to be
    sealed.
- **Detected by.** Never explicitly. The September compartment design made
  the question moot.
- **Counterfactual.** This is a process matter. The plan itself prescribed
  the remedy: an explicit decision to accept a warning-grade target.
  `PROJECT_WORK_ANALYSIS.md` l.444 flagged the general risk of "retrospective
  gate tuning" without finding this instance.
- **Cost.** Claim scope. The paper's packet-centred division of labour
  rested on a criterion that was never met, and the addendum still states
  that it "holds" (l.87–88).
- **Candidate lesson.** When a stated acceptance criterion keeps failing, the
  choices are to change the design or to record a dated decision that relaxes
  the criterion and narrows the claim. Replacing a failed metric with an
  assignment residual turns a failed test into an untested claim, because the
  residual of assigning a known tensor to fitted components is zero by
  construction.
- **Generality.** The first half is generic research hygiene
  (pre-registration), close to a truism. The second half, that assignment
  residuals cannot fail, is specific to source-decomposition work and worth
  a sentence.
- **Recurrence.** n = 1 clear instance, related to I-04 and I-10.
- **Evidence strength.** Strong.

## I-06 V5 support shell frozen at amplitude 1e-7: a cost-only objective selected a null component

- **Date, commit.** 17 May: `f0d709f` at 07:55 (the 4D ledger enters the
  harness), `1e0ec81` at 08:22 (freeze), `2747963` at 08:55 (4D sweep).
- **What happened.** At 01:31 the routing screen had concluded "not yet
  architecturally routed" (`V5_CARRYING_FLOW_ROUTING_SCREEN.md` l.135). The
  freeze selected amplitude +1e-7 on the reduced ADM ladder. Its incremental
  δj_l routing fraction into catch/support was 0.9928, the packet fraction
  3.19e-7, and all 54 sweep variants passed (PROJECT_WORK_ANALYSIS l.159–160).
  The freeze report itself notes that the lowest score was the smallest
  amplitude, "a minimal-intervention preference induced by the score's
  total-burden penalty" (`V5_SUPPORT_SHELL_FINAL_FREEZE.md` l.22). The 4D
  sweep then found the frozen amplitude "effectively invisible in the 4D
  source ledger" (`V5_CONTINUOUS_SUPPORT_SHELL_4D_SOURCE_SWEEP.md` l.148). At
  amplitude 1.0, radial-null burden rose 13.4% and the worst point peak by a
  factor of 2.54 (l.208). The single-channel overlay therefore fails as a
  "standalone load-bearing" mechanism (l.5). Plan.md l.2821 calls this "an
  overly optimistic interpretation" that the sweep corrected. The V10 edge
  check later adds that "the earlier tiny support-shell target surviving V10
  should not be generalized" (`STAGE1_V10_SELECTED_CANDIDATE_EDGE_CHECK.md`
  l.86).
- **Detected by.** The full demanded-tensor ledger, which had been available
  for 27 minutes when the freeze was made.
- **Counterfactual.** Trivially catchable: run the committed 4D ledger before
  freezing.
- **Cost.** Small: about 8 commits of reduced-harness screening in one
  night, reversed within 33 minutes.
- **Candidate lessons.**
  1. An objective that charges added burden and credits no delivered function
     is minimized by the null design. Check the effect size of any selected
     component.
  2. The routing fraction of an infinitesimal increment is a linear-response
     property and says nothing about load-bearing at working amplitude.
  3. Freeze on the complete demanded tensor, not on a reduced proxy (links to
     P01 2b).
- **Generality.** Lessons 1 and 2 are general optimization and linearization
  hygiene, close to truisms, but this is a crisp instance. Lesson 3 is
  general.
- **Recurrence.** Lesson 1: n = 1. Lesson 3 (proxy versus complete tensor):
  n = 3, namely this incident, the J component classification (P01) and the
  ANEC residual (I-10).
- **Evidence strength.** Strong.

## I-07 Legacy V10 freeze on an under-resolved cliff with zero speed headroom

- **Date, commit.** The work predates the repo; the bundles were imported on
  16 May (`60d6974`). The freeze was reversed from 17 to 23 May.
- **What happened.**
  - The 21×37 grid found the safety boundary "very sharp": w_th = 0.569 safe,
    0.570 failing (`RADIAL_PRESSURE_BOUNDARY_FINDINGS.md` l.30). The report
    advises promotion "with margin", then promotes 0.569 anyway (l.32–38,
    53).
  - The 41×73 grid found failures at 0.569, 0.565, 0.550 and 0.540: "the
    previously reported safety cliff was therefore under-resolved"
    (`HIGHRES_BOUNDARY_REPORT.md` l.129–135).
  - A lapse cushion (η_N = 2) restored 0.569 (`COMPENSATOR_HIGHRES_REPORT.md`
    l.42–44). The robustness study called the result a "thin tuned ridge"
    (`ROBUSTNESS_FINDINGS.md` l.79).
  - The V sweep found the last safe V = 10.00 and the first unsafe 10.01 on a
    101×181 packet-norm grid (`V_SWEEP_FINDINGS.md` l.62–66, 81).
  - The freeze was then declared as a "tuned V=10 reduced-geometry freeze
    candidate" (`FREEZE_REPORT.md` l.3–7, 68–72). Its live-packet Tkk fraction
    was 22.81% and its p_l fraction 27.06% (l.54–55), from 260 sampled live
    points.
  - Reversal: on 17 May Stage I-C fails at V10 (3 positive live
    packet-norm samples, maximum 37,140, 30.7% live radial-null fraction). On
    18 May the "target hierarchy [is] restored" with V5 primary and V10 an
    edge target (`STAGE1_RELEASE_CHOREOGRAPHY_REFREEZE.md` l.5–11), and a V10
    smoke test fails (l.154). On 23 May the V10 ladder finds 123 positive
    samples with a maximum of 1135.5
    (`STAGE2_BETA075_SERVICE_RATING_LADDER_DIAGNOSTIC.md` l.215–216). The
    stale V10 root files were deleted on 23 May (`1d90d2f`) after the review
    flagged them (`PROJECT_WORK_ANALYSIS.md` l.10, 58).
- **Detected by.** Grid refinement, then the Stage I worldtube report and
  the service-rating ladder.
- **Counterfactual.** The thin headroom was known when the freeze was made
  (V_SWEEP l.81), so the freeze was knowing. The refinement habit had already
  caught the 0.569 cliff once. Promotion at 21×37 preceded refinement.
- **Cost.** Moderate. The whole May V5 program used the V10-edge-tuned
  geometry (`tuned_w0569_eta200`) as its base variant (plan.md l.2823–2834),
  and root documents were stale for a week.
- **Candidate lesson.** A boundary located by sampled sign changes of a
  causal quantity moves under refinement. Promote only after refinement and
  with explicit margin, and never freeze at the edge the search discovered.
  Most of this is an engineering truism (margins, convergence). The
  domain-specific content is that passenger timelikeness is a sign test on a
  sparse sample (260 points) whose zero set lies between samples.
- **Generality.** General.
- **Recurrence.** "Sign boundaries lie between samples": n = 4. The
  instances are the w_th cliff; the V cliff; the GZ branch zero "between
  sampled points" (`STAGE2_GZ_OBSTRUCTION_SCREEN.md` l.88); and the September
  Type IV bands (P01).
- **Evidence strength.** Strong.

## I-08 Burden reduction repeatedly consumed the passenger's causal margin

A recurring pattern rather than a single event. It appears in:

1. Legacy V sweep: "radial softening and lapse cushioning improved source
   burden but spent a lot of V headroom". The shaped baseline was safe to
   V ≈ 12.0, the tuned branch to 10.00 (`V_SWEEP_FINDINGS.md` l.85).
2. "Uniform radial widening helps pressure but rapidly eats packet safety
   margin" (`HIGHRES_BOUNDARY_REPORT.md` l.135).
3. The packet carve: "At V10, nonzero carve strengths … worsen packet-norm
   safety, even while improving hard-channel placement" (plan.md l.3086).
4. The deep annular carve gives the lowest live fractions and 165 positive
   live packet-norm samples at V10 (plan.md l.3288).
5. The V2 near-pass branch fails the V5 cap on packet norm; three costs trade
   against each other (`STAGE1_V2_LOW_SERVICE_GATE_MEMO.md` l.62, l.83–88).
6. Moving the beta rematch later causes a V5 packet-norm failure
   (`STAGE1_RELEASE_CHOREOGRAPHY_REFREEZE.md` l.98–105).
7. September: the e⁴ plateau chosen to clear Type IV gives a 55× occupant
   clock (P01 2i).

- **Detected by.** The packet-norm gate, every time. The lapse cushion was
  introduced as a pure causal-margin compensator ("not the source-reduction
  knob itself", `COMPENSATOR_HIGHRES_REPORT.md` l.56).
- **Mechanism.** The packet norm −α² + γ_ll(v + β)² and the demanded stress
  depend on the same fields. Softening the support (smaller gradients,
  larger γ_ll) lowers the stress and raises the γ_ll(v + β)² term.
- **Candidate lesson.** Carry the passenger's causal margin, and later the
  occupant quantities, inside the same objective as the source burden. A
  post-hoc gate turns optimization into a search for the gate's edge (I-07).
- **Generality.** Plausible for shift-borne transport generally, through the
  mechanism above. It is demonstrated only in this design family.
- **Recurrence.** n = 7, which supports N01 ("optimizing to a single gate
  distorts other requirements") well beyond its single P01 incident.
- **Evidence strength.** Strong.

## I-09 Fraction metrics improving by moving the denominator

A recurring pattern that was mostly caught.

1. Moving R_th outward "improves fractions and peaks, but not absolute live
   radial burden" (`RADIAL_PRESSURE_SOFTENING_FINDINGS.md` l.64).
2. Spatial-split variants were "mostly moving denominators and peak
   locations" (`BIFURCATION_INTERIM_DECISION.md` l.26).
3. R = 2.0 "improves … fractions … by making a larger infrastructure ledger"
   (`POINT_LEVEL_FINDINGS.md` l.107).
4. Radius 2.05 raised assigned radial-support burden by 43%
   (`GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md` l.32).
5. The entry gate lowered live burden by dropping cells (I-04).
6. The 1e-7 routing fraction (I-06).
7. Domain enlargement changes raw totals, so live fractions become the
   comparison (`STAGE2_FULL_GRID_SOURCE_DECOMPOSITION_ENTRY_GATE.md` l.110).

- **Candidate lesson.** Report absolute burden alongside every fraction; a
  fraction gain that comes from a larger infrastructure ledger or domain is a
  denominator effect.
- **Generality.** General metric hygiene, a truism. Its value here is that
  the Stage I-B gate itself was defined as a fraction (I-05).
- **Recurrence.** n = 7. The practice worked in instances 1–3.
- **Evidence strength.** Strong.

## I-10 Finite-domain ANEC negative on the demanded total; the residual was ablated

- **Date, commit.** 23 May 18:51, `bf1619c`,
  `STAGE2_BETA075_FINITE_DOMAIN_RADIAL_ANEC_DIAGNOSTIC.md`. This came after
  the 22 May 21:26 seal (`8dab55f`).
- **What happened.** The run took 72.3 s for 3,452 traces (l.58). On the
  minus branch, 1,495 of 1,701 traces are negative, with worst −1.797 and
  median −0.067 (l.62). The dominant negative sector is
  `sector_closure_residual` in 3,413 traces (l.69–72). Ablating the residual
  and then `live_handoff_trim` (l.85, 111) leaves the non-live sectors "close
  to finite-domain radial-ANEC balanced" (l.125). The interpretation says
  the result is neither "ANEC passes" nor "killed", names "the unresolved
  closure/completion layer" as the principal issue, and sets the next work as
  "source-basis completion" (l.131–152). The rule pre-registered on 23 May
  (plan.md l.935–936, 952–955) offered only source-side remedies.
- **What is wrong.** The closure residual is the part of G/8π that the named
  sectors do not cover. Setting it to zero evaluates a different tensor, and
  ANEC along null geodesics belongs to the geometry's demand. **Inference
  (weak–moderate):** for a traversable two-ended geometry, topological
  censorship (Friedman–Schleich–Witt 1993) requires ANEC violation along some
  complete null geodesic through the throat. The negative result is
  therefore what I-01 predicts, although these finite-domain traces do not
  establish it.
- **Detected by.** Not re-adjudicated. The geometry was superseded. September
  practice maps ANEC along complete rays (`e744879`).
- **Counterfactual.** 72 s on machinery available since 19 May. Running it
  before the seal would have put an ANEC-negative demanded total on record
  before sealing.
- **Candidate lesson.** Energy-condition verdicts belong to the complete
  demanded tensor, and ablating a bookkeeping component changes the tensor
  under test (the same claim as P01 2b). A second lesson: SNEC-clean and
  ANEC-negative on the same traces (see CE-8) means a finite-window
  benchmark can pass where the averaged condition fails, so the claim must
  name which condition it rests on.
- **Generality.** High.
- **Recurrence.** "Component or residual manipulation instead of
  complete-tensor verdict": n = 3. The instances are the J regulator (P01),
  this ablation, and the "live residual" substitution (I-05).
- **Evidence strength.** Strong for the facts; moderate for the judgment;
  weak for the topological-censorship link.

## I-11 Seal before off-design tests: the closure fit held only at its calibration point

- **Date, commit.** 22 May (support-stroke and total-closure fits, seal
  `8dab55f`) and 23 May (`c4d7aba`, `d683753`, rescoped by `c73f8d2`).
- **What happened.**
  - Dense-mesh basis ladder (`STAGE2_BETA075_MATTER_ACTION_FEASIBILITY_WORKLOG.md`
    l.1280–1330, 1536–1557):
    - 12×8 and 16×10 fail;
    - 20×12 near-fails (0.512–0.524 against a 0.50 gate);
    - 22×13 passes the aggregate gate and fails the local one
      (0.5975/0.581 against 0.55);
    - 24×14 passes, with an effective coefficient count of about
      13,000–13,900 against a gate of 18,000 (l.1100–1110).

    The worklog read this as "support/radial-edge resolution".
  - Total closure passes with residual/endpoint L2 = 0.451 against a 0.55
    gate, and a local margin of 0.544567/0.55 (PROJECT_WORK_ANALYSIS l.394;
    `STAGE2_BETA075_SUPPORT_SECTOR_ROBUSTNESS_GATE.md` l.22, fractional
    margin 0.009878).
  - Seal: "15 gates, 0 hard blockers" (plan.md l.668).
  - The next day V = 2.5 is source-safe but the medium/support closure fails,
    because it is "tuned narrowly around the V=5 operating point"
    (`STAGE2_BETA075_SERVICE_RATING_LADDER_DIAGNOSTIC.md` l.23–33). V = 10
    fails as well. The disclosure is rescoped to "an operating-point seal …
    rather than a service-family theorem" (`c73f8d2` message).
- **Detected by.** The service-rating ladder, the first off-design test.
- **Counterfactual.** The same harness, rerun at V = 2.5 before sealing:
  hours of compute (dense 377×241).
- **Cost.** A one-day scope reversal. The larger cost was the confidence the
  seal conveyed (CE-4).
- **Candidate lesson.** A source closure fitted to a known demand needs
  out-of-sample tests before any claim of closure: off-design service
  points, and mesh-independence of the basis it needs. A required basis that
  grows with mesh density indicates a fit to the demand, not a source law. A
  closure criterion that tolerates residuals of 45–55% of the signal is weak
  and should be named as such.
- **Generality.** General model-validation practice, a truism in statistics.
  The domain point is that the demand G/8π is always known, so a flexible
  enough basis always "closes"; only out-of-sample tests carry evidence.
- **Recurrence.** n = 3: the V2.5 closure, the basis escalation, and the
  J regulator added to fix the type (P01).
- **Evidence strength.** Strong for the facts; moderate for the reading of
  basis growth, which is mine.

## I-12 "Hard-affine" SNEC used the lapse parameter

- **Date, commit.** 19 May (`00f6c4d` onward) to 21 May (`9316c67`,
  `STAGE2_AFFINE_REPARAM_SNEC_AUDIT.md`).
- **What happened.** The traces advanced dλ = α dσ while the reports called
  the result "hard-affine" (l.7–12). Following a critique, the non-affinity
  was computed: κ has median 6.1 and maximum 105, and dλ/dσ reaches 1,291
  (l.126–133). The verdict held (175,851 windows, zero violations), and the
  wording was corrected (l.127–138).
- **Counterfactual.** The error was in the definition from the start; the
  geodesic equation was the tool.
- **Cost.** Small: one rerun of 1,604 s.
- **Candidate lesson.** Averaged and smeared null conditions are defined
  with affine parameters. In lapse- and shift-dependent metrics, coordinate
  or lapse parameters differ from affine ones by large factors, so the
  non-affinity should be computed and reported.
- **Generality.** Textbook physics.
- **Recurrence.** n = 1. The decision did not change.
- **Evidence strength.** Strong.

## I-13 Domain truncation hid failures and manufactured others

A recurring pattern.

1. The V5 4D overlay needed an expanded s range "so the leading catch/support
   window is not clipped" (`V5_CONTINUOUS_SUPPORT_SHELL_4D_SOURCE_SWEEP.md`
   l.62).
2. At τ = 4, SNEC failures were boundary truncation; a scoreable-window rule
   and an extended domain removed them (`STAGE2_HARD_AFFINE_SNEC_ADVERSARIAL.md`
   l.78, 111, 151).
3. The same extension exposed real early-entry packet-norm positives (I-04).
4. The GZ smoke traces "hit the upper sigma boundary", which the screen
   called inconclusive (`STAGE2_GZ_OBSTRUCTION_SCREEN.md` l.115).
5. Packet-centreline probes, 24 of 24, and all 41 red-tag reset-tail traces
   end at the future boundary (`STAGE2_SCHEDULED_ADM_PROBE_EVOLUTION_PILOT.md`
   l.75, 88); confidence runs were extended to s = 12 and s = 15.
6. The finite-domain ANEC is limited to the longest in-domain traces (I-10).
   September replaces it with complete rays.

- **Candidate lesson.** Evaluate on a domain that contains the whole service
  and the full extent of every ray and window used. Flag truncated
  evaluations as unscoreable, and extend the domain until verdicts stop
  changing. In time-dependent services with tilted cones, traces are long and
  setup phases sit early, so small (s, l) boxes clip both.
- **Generality.** General numerical practice, close to a truism, with
  domain-specific reasons.
- **Recurrence.** n = 6. The practice worked in instances 2–3, but its
  output was then reclassified (I-04).
- **Evidence strength.** Strong.

## I-14 Central rays escaped while their neighbours focused

This is a check that caught a problem early.

- **Date, commit.** 21 May, `59f97c4`,
  `STAGE2_DENSE_CONGRUENCE_CAUSTIC_AUDIT.md`.
- **What happened.** The central traces recovered and escaped. Dense
  bundles around them also escaped (136 of 136 rays), but 8 of 8 bundles
  showed caustic-like compression, with a minimum all-shrinking width of
  0.008–0.010 in l (plan.md l.1732–1737; audit l.62, 151). The promotion
  criterion failed, and the response was the collar repair
  (`rematch_w6_t1p5`, 0 of 8).
- **Candidate lesson.** Causal-structure claims from ray tracing need finite
  congruences and their expansion; single rays are insufficient.
- **Generality.** General; it follows from Raychaudhuri focusing.
- **Recurrence.** n = 1 as a decision-changer; the practice was kept in
  September.
- **Evidence strength.** Strong.

## I-15 Knob tuning before term attribution; the channel-cause ledger redirected it

- **Date, commit.** 18 May, `e842f01`,
  `STAGE1_CHANNEL_CAUSE_LEDGER_FINDINGS.md`.
- **What happened.** From 17 May (`3de5b48`) to 18 May (`a55fc98`), about 15
  commits swept carve, lapse, beta-rematch, shoulder and release knobs. The
  cause ledger, a postprocess of existing ledgers, found the top bad points
  "overwhelmingly radial-metric dominated, not beta-gradient dominated"
  (plan.md l.2742). It pointed away from stronger beta rematch and
  coordinated release and toward "refining the radial support law itself"
  (l.152–164).
- **Counterfactual.** Cheap and available earlier: the ledger already held
  the fields.
- **Cost.** About 1–1.5 days of knob sweeps, partly informative.
- **Candidate lesson.** The demand is a known differential expression of the
  metric functions. Attribute failing points to term families (lapse
  curvature, shift gradient, radial metric, angular capacity) before adding
  knobs.
- **Generality.** General for metric-first design, where attribution is
  always available.
- **Recurrence.** n = 3: this incident; plan.md l.2758 ("term-level
  decomposition … before adding another design knob"); and September
  attribution by ablation (decompression alone gives 874 Type IV points,
  THROAT_GEOMETRY_CLARIFICATION l.153–158).
- **Evidence strength.** Moderate–strong.

## I-16 Wiring bug caught by a reproduction check

- **Date, commit.** 19 May, `b5ea657`, `STAGE1_SMOOTH_SPLIT_ANSATZ_PROGRESS.md`
  l.86–110.
- **What happened.** The `additive` selector was applied only to the outer
  carve stack while the inner composition stayed `smooth_union`. The result
  was an under-carve that "falsely suggested that the smooth family was
  intrinsically worse". After the fix, the additive reference reproduces
  `split_ref` exactly on six metrics.
- **Candidate lesson.** A new parameterization that nests the old design
  must reproduce it exactly before any comparison. This is a software truism.
  Its value here is that it prevented the rejection of a design family.
- **Recurrence.** n = 1 recorded. Related habits are the default-off
  switches that keep historical semantics (`live_packet_start` unset, `tanh`
  defaults).
- **Evidence strength.** Strong.

## I-17 Claim labels ran ahead of evidence

1. "Hard-affine" SNEC (I-12).
2. On 23 May `695ab76` and `0047ad3` call the 3+1 run a "capstone" and
   declare Stage II "locally mature". It is demoted to a "light proxy" the
   same day (`27837dd`, `dc4e95a`;
   `STAGE2_BETA075_3P1_BACKREACTION_CAPSTONE.md` l.7–14).
3. The 23 May closeout says the package "passed … physical source-family,
   action-level fixed-background PDE …" (plan.md l.902–909). The review
   judged "physically viable" "too strong unless qualified" and flagged the
   tone of "physical-viability architecture" (PROJECT_WORK_ANALYSIS
   l.598–600, 71).
4. The May paper says its results "increase confidence" (addendum issue 6,
   l.79–81).

- **Candidate lesson.** Name each result after the check it passed
  (fixed-background, prescribed-metric, finite-window). Words like capstone,
  seal, certificate and theorem imply coverage.
- **Generality.** A truism. It is mostly a project habit and earns a
  sentence in the book.
- **Recurrence.** n = 4. Items 1–3 were caught within days; item 4 four
  months later.
- **Evidence strength.** Strong.

## I-18 Superseded claims persisted

1. The root files still claimed the V10 "final refreeze" until 23 May
   (`1d90d2f`). The review had flagged document drift and "multiple
   generations of 'final' language" (PROJECT_WORK_ANALYSIS l.10, 58, 633).
2. Report status text was stale (l.575–576).
3. The service-time ratios were still carried on 23 Sep, one day before
   their retraction (plan.md l.72–74).

- **Candidate lesson.** Keep a supersession map. This is document control,
  a truism, and gets one sentence.
- **Recurrence.** n = 3.
- **Evidence strength.** Strong.

## I-19 White Casimir: morphology before magnitude

- **Date, commit.** From 29 May (`521eb3e`) to 30 May (`8d55a8c`,
  `4123694`, `a4d378b`).
- **What happened.**
  - The protocol orders the morphology reproduction (Stage 3) before the
    source-demand magnitude ratio (Stage 6), which it calls "a hard
    interpretation gate" (`white_casimir_intersection/white_casimir_source_function_audit_protocol_realigned.md`
    l.297, 483–502).
  - On 29 May: smoke test (625 of 625 pixels negative, a scoring-rule effect;
    `WHITE_CASIMIR_V_LOOP_GLOBAL_NEGATIVITY_READ.md` l.36), then v-loop, then
    scale-separated discrimination, then the fidelity probe. The morphology
    paper followed at 18:50 (`e1f6956`), with three more paper commits. The
    abstract defers SI normalization "to later calculation layers".
  - On 30 May at 10:58, the tensor-scale probe (6,744.7 s) gives a best
    source-demand ratio of about 1.02e-39 and a timing bound of about
    7.81e-76 s (`WHITE_CASIMIR_TENSOR_SCALE_PROBE_FINDINGS.md` l.24–30, 66).
    The verdict becomes "does not support a warp-functional source claim at
    physical scale", and the paper is revised at 12:16.
  - At 12:35 the Stage 4 synthetic discrimination runs anyway, and "does not
    change the physical scale conclusion" (`WHITE_CASIMIR_STAGE4_SYNTHETIC_DISCRIMINATION.md`
    l.16–26). Stage 5 then pivots to Casimir-boundary readouts (force and
    cavity shifts), which is a different claim.
- **Counterfactual.** Minutes with a pencil. The parallel-plate energy
  density at a = 1 µm is about −4×10⁻⁴ J/m³. The Alcubierre scale
  c⁴/(8πG w²) for a micron wall is about 10⁵⁵ J/m³, a ratio far below
  10⁻³⁰. This is my rough estimate; I have not reproduced the harness's 1e-39
  normalization.
- **Cost.** Small: about one day, about 15 commits, and one paper draft
  revised.
- **Candidate lessons.**
  1. For any proposed source of exotic stress, compute the order-of-magnitude
     supply-to-demand ratio before morphology or placement work. A shape
     match cannot compensate for a tiny ratio.
  2. Stop the ladder when a hard gate closes.
- **Generality.** High. The Casimir-versus-warp magnitude gap is known in
  the literature, for example Pfenning & Ford 1997 on wall thickness; **to
  verify**.
- **Recurrence.** Lesson 1: n = 3, all "the magnitude check came late": this
  incident; September's finding that a Casimir mirror carries about 10⁷ times
  its deficit (`SOURCE_SCALING_TEST.md` l.23–29); and September's quantum
  field count N ≥ Q(L/ℓ_P)², found after the May SNEC benchmark was run in
  rail units with no scale (l.15–22, 175–177;
  `STAGE2_HARD_AFFINE_SNEC_PROMOTED_PAIR.md` l.42). Lesson 2: n = 1.
- **Evidence strength.** Strong for the sequence; moderate for the
  counterfactual estimate.

## I-20 Scalar kill screen (a check that worked)

- **Date, commit.** 19 May, `16c6a67` and `8bbff98`.
- **What happened.** A Barceló–Visser-like scalar was tested against the
  promoted pair. A localized solve ran 80 iterations in 124 s. Radial-null
  coverage was 7.8e-6, and the scalar placed its negative Tkk in
  reset/decompression, away from the demanded rows (plan.md l.2648;
  `STAGE2_PROMOTED_PAIR_SCALAR_KILL_SCREEN_PROGRESS.md` l.150–173). The
  scalar search stopped.
- **Candidate lesson.** Audition the simplest source family cheaply against
  the full demand pattern, including placement and timing, before widening
  the search.
- **Caveat.** The pivot went to oracle decomposition (CE-3), so the check
  worked but the follow-up practice misled.
- **Recurrence.** n = 2, counting the September scale tests that excluded
  quantum fields, Casimir cavities and curvature-coupled scalars.
- **Evidence strength.** Strong.

---

## P01+ Additions to incidents already documented in P01

These additions strengthen P01's counterfactual. The Type IV signature was
present in May data from 17 May, and on 20 May it was described in words.

- **17 May `f0d709f`.** Every ledger row records `Tkk_plus` and `Tkk_minus`
  (`source_ledger.py` at that commit, l.287–300). The badness channel keeps
  only min(Tkk_plus, Tkk_minus) (l.343–344), which discards the sign of the
  product. For the radial block, Type IV holds exactly when
  T(k₊,k₊)·T(k₋,k₋) < 0 (`CONSTANT_RADIUS_TRACK.md` l.37–46). In spherical
  symmetry the radial block fixes the type, so the test was one line on
  existing columns.
- **18 May `e842f01`.** The channel-cause ledger records ρ_H + p_l and 2j_l
  side by side (`STAGE1_CHANNEL_CAUSE_LEDGER_FINDINGS.md` l.26–40). The
  radial-block Type IV criterion is |ρ + p_l| < 2|j_l|.
- **20 May `fc6a03c`.** In the reset/decompression cap, "one-branch-negative
  share: 75.6%" and "both-branches-negative share: 2.7%"
  (`STAGE2_ENDPOINT_THEORY_MEMO.md` l.44–51). The memo reads this as "a
  current/branch-selected endpoint relaxation problem" (l.53–55). One radial
  null energy negative with the other positive is the Type IV signature, and
  the addendum later attributes the Type IV layer to exactly this
  decompression step (addendum l.64–70; decompression alone gives 874 Type IV
  points, THROAT_GEOMETRY_CLARIFICATION l.153–158).
- **Accounting frame.** The legacy refreeze report states "The live passenger
  accounting ends before reset/decompression. Reset is infrastructure work,
  not passenger exposure" (`FINAL_REFREEZE_AND_SOURCE_REPORT.md`, deleted in
  `1d90d2f`; `git show 1d90d2f^:FINAL_REFREEZE_AND_SOURCE_REPORT.md`). The
  phase kept out of passenger scrutiny is where the inadmissible stress
  lived (see CE-7).

The lesson "an information-destroying reduction (min over branches) can hide
the diagnostic you need" is general. It recurs in the September
node-sampling incident, where sampling reduces a continuum to nodes. Here
n = 2.

---

## Counter-evidence: practices that were followed and did not help, or misled

- **CE-1 An internal quality review that graded the process inside the frame.**
  `PROJECT_WORK_ANALYSIS.md` (23 May) rates phases "Very strong" (l.392) and
  shows "Excellent corrective discipline" (l.488). It calls the reports
  "unusually good as a research log" (l.563) and takes repeated demotion of
  overbroad claims as the "strongest evidence of quality" (l.631). Its
  list of the "strongest unsupported" claims (l.20–24) contains no mention
  of topology, wormholes, Hawking–Ellis type or packet kinematics; a grep of
  the file finds none of these terms. It correctly flagged claim tone, gate
  tuning and document drift. A review that checks process and wording does
  not test the frame; a frame review asks what the geometry is globally, what
  type the whole tensor has, and where the passenger actually is. *Strong.*
- **CE-2 Gate count and certificate depth were not coverage.** The seal
  matrix had 15 gates, 0 hard blockers and 5 required watches (plan.md
  l.668). Beyond it came principal-symbol, rapidity, energy-certificate and
  discretization-robustness certificates, and a moderate 3+1 capstone with
  218,400,768 rows (plan.md l.892). All of it ran on a geometry that is
  two-ended and carries 13,587 Type IV points, with the passenger evaluated
  off its worldline. Numerical convergence confirmed quantities that answered
  the wrong questions. Depth within one class of failure did not substitute
  for breadth across classes: algebraic type, topology, kinematics and
  causality. *Strong.*
- **CE-3 Oracle source-role partitions produced a progress signal without
  evidential weight.** They assigned 98.659% of radial-null burden, 98.716%
  of radial pressure and 91.315% of angular pressure (plan.md l.1920).
  Components multiplied as A–G, then H, I, J, R, C_live and D_H. The project
  itself labelled this "an oracle assignment" and "an oracle partition, not a
  physical stress tensor" (`STAGE2_COMPONENT_SOURCE_LEDGER_PROMOTED_PAIR.md`
  l.20, 152), and still used it as progress. The partitions enabled the
  "live residual" substitution (I-05) and the residual ablation (I-10).
  Assigning a known tensor always succeeds. *Strong.*
- **CE-4 Freezes and seals did not hold.** In 16 days: the V10 freeze was
  reversed; the V5 shell freeze was superseded in 33 minutes; the beta075
  seal was rescoped the next day and superseded in September. The freeze's
  function, stopping local tuning, worked. The confidence it implied did not
  hold. *Strong.*
- **CE-5 Pre-registered decision rules with only source-side branches.**
  The ANEC rule (plan.md l.935–936, 952–955) anticipated a negative outcome
  but offered only source-side remedies. The actual outcome, dominated by the
  residual, fell outside its cases and was handled source-side (I-10). A
  pre-registration only helps when its branches include a geometry revision.
  *Moderate.*
- **CE-6 Careful non-claim language did not protect against frame errors.**
  Almost every report lists what it does not claim ("not a matter model",
  "not a theorem"), and the review praised this. Those caveats name missing
  depth inside the frame (matter action, RSET, 3+1) and never question the
  frame. *Moderate.*
- **CE-7 Passenger-centred zoning directed scrutiny away from
  infrastructure phases.** Reset and decompression sat outside passenger
  accounting (P01+). The fatal Type IV stress lived in that phase and was
  described in words on 20 May without consequence. Functional zoning is a
  candidate practice (P03), and this is an observed hazard for it. n = 1.
  *Moderate.*
- **CE-8 Large window counts on a permissive benchmark.** SNEC scans of
  60,393, 120,918, 175,851 and 203,838 windows found no violations (plan.md
  l.1920, l.1730), while ANEC on the same traces was negative (I-10). The
  benchmark was evaluated in rail units with B = 1/(32π) and no physical
  scale. The review listed it among "results that look strong" (l.532).
  Sample size is not evidence against a structurally different failure.
  *Moderate.*

Practices that did help, for balance, are mostly standard numerical hygiene:

- extended-domain adjudication with scoreable-window rules (I-13);
- dense bundles (I-14);
- the scalar kill screen (I-20);
- the reproduction check (I-16);
- matched-strength shape comparison (`V5_SUPPORT_SHELL_SHAPE_ROBUSTNESS_REPORT.md`
  l.3, 117);
- regenerating the tensor after a post-processed metric edit
  (`STAGE2_BETA_COLLAR_GENERATOR_SCREEN.md` l.7–15);
- the seam-artifact check (`STAGE1_RELEASE_CHOREOGRAPHY_ARTIFACT_CHECK.md`
  l.5, 122–130);
- declaring a discriminator "not decision-grade"
  (`V5_SIGNED_SOURCE_OBJECTIVE_SIGN_TEST.md` l.34).

---

## Closing table

| Incident | Candidate lesson | n | Generality | Evidence |
|---|---|---:|---|---|
| I-01 Unstated two-ended topology | State the global structure (ends, topology, formability from ordinary space) before engineering; a spherical reduction with the track as radial proper distance and R > 0 is a wormhole | 1 (5 missed checks) | High; established physics (Geroch, topological censorship) | Strong |
| I-02 Two packet readings | One prescribed passenger worldline; every passenger audit on it; the window centre follows the carry velocity | 1 root, 4 manifestations | High | Strong |
| I-03 Service-time advantage | Arrival claims compare packet and light events through the same spacetime; transport-parameter distances are circular | 1 | High; literature exists (to verify) | Strong |
| I-04 Entry-gate reclassification | Redefining passenger exposure needs a worldline-based justification; vanishing failures with unchanged geometry are relocated | 4 (incl. I-05, I-10, P01 regulator) | Medium–high | Strong facts / moderate judgment |
| I-05 Gate erosion and metric substitution | Relax a failed criterion only by explicit dated decision; assignment residuals are zero by construction | 1 | General (truism) + domain point | Strong |
| I-06 Null component frozen | Cost-only objectives select null designs; linear-response fractions do not show load-bearing; freeze on the full tensor | 1 (proxy vs full: 3) | General | Strong |
| I-07 V10 freeze at an under-resolved cliff | Sampled sign boundaries move under refinement; refine and keep margin before promoting | 4 | General (mostly truism) | Strong |
| I-08 Burden vs causal margin | Carry causal margin and occupant quantities in the same objective as source burden | 7 | Plausible for shift transport; shown in one family | Strong |
| I-09 Fraction metrics | Report absolute alongside fractions; denominators move | 7 | General (truism) | Strong |
| I-10 ANEC residual ablation | Energy-condition verdicts belong to the complete tensor; name which condition a claim rests on | 3 | High | Strong / moderate; topology link weak |
| I-11 Seal before off-design | Out-of-sample tests for fitted closures; basis growth with mesh signals a fit | 3 | General (truism) + domain point | Strong / moderate |
| I-12 Lapse parameter as affine | Compute non-affinity; averaged null conditions need affine parameters | 1 | Textbook | Strong |
| I-13 Domain truncation | Domain must contain the full service and ray extents; flag truncated evaluations | 6 | General (near truism) | Strong |
| I-14 Dense bundles | Congruences, not single rays | 1 | General | Strong |
| I-15 Term attribution before knobs | Attribute failures to metric-function term families before adding knobs | 3 | General for metric-first design | Moderate–strong |
| I-16 Wiring bug | Nested parameterizations must reproduce the reference exactly | 1 | Truism | Strong |
| I-17 Label inflation | Name results by the check passed | 4 | Truism / project habit | Strong |
| I-18 Stale claims | Supersession map | 3 | Truism | Strong |
| I-19 White Casimir | Supply–demand magnitude first; stop the ladder when a hard gate closes | 3 / 1 | High | Strong / moderate |
| I-20 Scalar kill screen | Cheap audition of the simplest source family against the full demand pattern | 2 | High | Strong |
| P01+ Type IV in May data | Information-destroying reductions (min over branches) hide diagnostics; the signature was in words on 20 May | 2 | General | Strong |
| CE-1 Frame-blind review | Process reviews do not test the frame; frame review is a separate act | 1 | General | Strong |
| CE-2 Gate depth ≠ coverage | Breadth across failure classes before depth | 1 (pervasive) | General | Strong |
| CE-3 Oracle partitions | Assignment of a known tensor always succeeds; it is not evidence | 1 (pervasive) | High for source decomposition | Strong |
| CE-4 Freeze/seal rituals | Freezes stop tuning; they carry no confidence | 3 | General | Strong |
| CE-7 Zoning hazard | Passenger-centred zoning left infrastructure phases unscrutinized | 1 | Hazard for P03 | Moderate |
