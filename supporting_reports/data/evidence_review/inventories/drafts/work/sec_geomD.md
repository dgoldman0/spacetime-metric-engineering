### 3.D Endpoint, release, receiver, collar and causal knobs (Stage II, May 19 – 24)

Stage II works on the entry-gated `wide4_start_m1p40` design and then on the
**beta075** geometry: release width 0.75, negative-l receiver `p003_mid`,
collar `rematch_w6_t1p5`. That frozen case,
`V5_smooth_split_horizon_escape_beta075_p003_mid_rematch_w6_t1p5`, is the one
that failed the Hawking–Ellis boundary gate (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:5-24`).
Entries marked **[β075]** rest on that geometry or on its release-0.75
predecessors.

The endpoint metric "J" is the selected radial-null deficit of the endpoint
layer. Selected margin = ρ + p_l − 2|j_l|; J = reset cap + support edge exactly
in every table (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:128-130`). The
receiver reports' one-sided "transfer" metric clips opposite-sign changes and
can disagree in sign with the raw J change; for example `post1p5` reports net
relief +0.0075 while raw J rises 0.9448 → 0.9493
(`STAGE2_NEGATIVE_L_RECEIVER_BETA100_RETIMING_LOCALITY.md:94-97, 129`). The
entries below use raw J. Baselines move with grid by amounts comparable to
many knob effects: J at release width 0.25 is 0.986686 (61×83), 0.990430 (81×121)
and 1.010455 (151×225) (Stage II endpoint extraction).

#### G22. Endpoint smearing: edge width, catch width, edge carve, guard blend, temporal width

- (a) Spatial width and strength of the compact carve windows at the
  support-edge handoff, and their temporal width.
- (b) Edge width 7.2 → 9 → 11; catch 3.4 → 4.2; carve 0.16 → 0.12; current
  guard blend 0.25; temporal ×1.0 → ×1.4, at release width 0.25 (81×121) and
  0.75 (61×83) (`STAGE2_ENDPOINT_THICKNESS_LADDER_CLOSEOUT.md:81-89`;
  `STAGE2_ENDPOINT_BETA_SUPPORT_CODESIGN.md:15-24`).
- (c) J 0.990430395 → 0.990415489 at edge width 11; every spatial variant
  moves J by ≤ 8.6×10⁻⁵; the reset cap stays 0.568413667 (0.568412635 with the
  guard) (`STAGE2_ENDPOINT_THICKNESS_LADDER_CLOSEOUT.md:130-137`). Temporal
  ×1.4 creates the only live defect: packet norm +16.81 at (σ, l) = (−0.769,
  −0.42), entry pre-catch (`:114-121, 138`). At release width 0.75 the reset
  stays 0.442605 across all variants (`STAGE2_ENDPOINT_BETA_SUPPORT_CODESIGN.md:178-185`).
  SNEC screen: 0 violations in 17,052 windows (`STAGE2_ENDPOINT_THICKNESS_LADDER_CLOSEOUT.md:227-233`).
- (d) SWEEP (5 + 5 variants, two grids).
- (e) DESIGN.
- (g) **Decoupling**: endpoint J is insensitive to the spatial thickness of
  the carve windows; "the effective burden fraction and current share stay
  effectively fixed" while the apparent volume changes (`:188-192`).
- (h) "the endpoint obligation is stubborn enough that the next model should
  not try to hide it by another mask smear" (`:262-264`). Temporal broadening
  pushes support action into the live pre-catch corridor.
- (i) [L2] for the live defect; the release-0.75 repetition is [β075].

#### G23. Release-fade width ("reset-release widening"), matched hold and lags

- (a) Duration of shift removal: the fade lasts 4·w_β·multiplier after a hold
  (`source_ledger.py:313-316`). The project names `beta025/050/075/100` are
  these multipliers.
- (b) Multiplier 0.25/0.50/0.75/1.00; hold 0.10/0.25/0.50; lapse lag and
  carve lag 0/0.25 (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:98-106, 141-143, 170-172, 185-202`).
- (c) (61×83; `STAGE2_ENDPOINT_BETA_SUPPORT_CODESIGN.md:130-139`)

| width | J | reset cap | reset current | support edge | support-edge current | support-edge p_Ω |
|---:|---:|---:|---:|---:|---:|---:|
| 0.25 | 0.986686 | 0.582542 | 0.318861 | 0.404144 | 0.060721 | 1.506623 |
| 0.75 | 0.964417 | 0.442605 | 0.240184 | 0.521812 | 0.105033 | 1.912497 |
| 1.00 | 0.944764 | 0.371175 | 0.177826 | 0.573589 | 0.133567 | 2.093173 |

  At 0.75: J −2.26%, reset −24.02%, reset current −24.67%, support edge
  +29.12%, support-edge current +72.98%, support-edge p_Ω +26.94%. About
  80–84% of the reset relief reappears in the support-edge shoulder
  (`STAGE2_ENDPOINT_BETA_SUPPORT_CODESIGN.md:157-164`). Reset-cap burden
  spreads: effective volume fraction 0.286 → 0.588 (0.75) → 0.780 (1.00)
  (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:211-213`). Hold 0.50: J 0.983927,
  reset 0.559395 (`:170-172`). Lags: "All three reproduce the baseline J split
  exactly at this precision" (`:185-186`). Live-clean at every width. Causal:
  post-release reachability hits 1 (0.75) vs 13 (1.00)
  (`STAGE2_HORIZON_REACHABILITY_AND_CAUSAL_GUARD_REPORT.md:193-194`).
- (d) SWEEP (4 widths, one grid); "needs confirmation on a denser grid"
  (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:264-265`).
- (e) DESIGN. **Type reading GEN-I**: the reset cap is 75.6%
  one-branch-negative (Type IV by I3) and the support edge 85.5%
  both-branches-negative (Type I NEC violation)
  (`STAGE2_ENDPOINT_THEORY_MEMO.md:36-49`). The knob converts current-selected
  (Type IV-like) reset deficit into support-edge load; the type of the
  transferred load was not measured.
- (f) Reset relief against support-edge load at ~80% transfer. The width also
  sets the receiver drive (w_rel − 0.25) and its timing
  (`source_ledger.py:559-576`), so release width, receiver dose and receiver
  phase move together.
- (g) **Decoupling**: only the release width moves the reset cap materially;
  "release beta width is load-bearing for endpoint source closure"
  (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:16`). Lapse and carve lags are
  fully decoupled from J.
- (h) Endpoint load follows the time profile of the shift removal, not the
  spatial thickness of the endpoint windows (contrast G22).
- (i) Width 0.75 is the beta075 geometry [β075][L1]; decompression is the
  Type IV generator acting on this reset cap (G5).

#### G24. Receiver actuation channel (lapse, radial stretch, shift relaxation, areal radius)

- (a) Which metric function a post-release support-edge "receiver" window
  edits: α, A, β toward comoving, or B (`source_ledger.py:1484-1562`).
- (b) Radial/current R1, positive-l angular R2, R1+R2; lapse 0.04, radial
  0.04, lapse+radial, lapse+radial+angular 0.015 (all release width 0.75)
  (`STAGE2_BETA_MEMORY_RECEIVER_SMOKE_MEMO.md:34-60`;
  `STAGE2_BETA_MEMORY_RECEIVER_LAPSE_RADIAL_MEMO.md:39-56`).
- (c)

| variant | J | support-edge current | support-edge angular |
|---|---:|---:|---:|
| baseline | 0.964417 | 0.105033 | 1.912497 |
| lapse 0.04 | 0.965803 | 0.104954 | 2.537997 |
| radial 0.04 | 0.965790 | 0.106144 | 1.941453 |
| lapse + radial | 0.967548 | 0.106048 | 2.464310 |
| lapse + radial + angular 0.015 | 0.954120 | 0.214547 | 2.566714 |
| R2 positive angular | 0.949838 | 0.551170 | 2.313310 |

  "The only tested knob that moves selected-null is angular capacity, and
  every tested positive-l angular realization has carried a current/angular
  penalty" (`STAGE2_BETA_MEMORY_RECEIVER_LAPSE_RADIAL_MEMO.md:72-75`).
- (d) SWEEP (9 variants). (e) Measured. **Direction GEN-I**: by I2 only an R
  edit changes the radial null energies directly; lapse and stretch enter
  them only through the null Hessian. A lapse-only edit raising angular stress
  33% is consistent with I16 (clock curvature X feeds p_t), which no report
  derives.
- (i) [β075] [L1] [L2].

#### G25. Receiver placement, angular gain, localization and persistence

- (a) Side of the throat (positive l, negative l, bilateral) and log gain of
  a post-release areal-radius flange at the support edge; its radial window
  (inner/outer multipliers, outer power), memory gain and post-release
  persistence (`source_ledger.py:559-630`).
- (b) Dose 0.0075/0.015 on each side (`STAGE2_BETA_MEMORY_RECEIVER_ANGULAR_SYMMETRY_MEMO.md:40-48`);
  negative-l 0.0075/0.015/0.0225/0.03 (`STAGE2_NEGATIVE_L_RECEIVER_LADDER_CLOSEOUT.md:40-60`);
  mid (0.50/1.025, power 0.5) vs outer at 81×121
  (`STAGE2_NEGATIVE_L_RECEIVER_PROMOTION_GATE.md:15-18, 46-56`); persistence,
  gain and localization variants at release width 1.00
  (`STAGE2_NEGATIVE_L_RECEIVER_BETA100_RETIMING_LOCALITY.md:55-100`).
- (c) Side at 0.015: positive J 0.957289 with support current 0.215404
  (+105%); negative J 0.954948 with current 0.107180 (+2%); bilateral 0.947820
  (`STAGE2_BETA_MEMORY_RECEIVER_ANGULAR_SYMMETRY_MEMO.md:43-45`). Negative-l
  dose: J 0.964417 → 0.959711 → 0.954948 → 0.950129 → 0.946962; reset cap
  0.442605 → 0.425718; support edge flat 0.5218 → 0.5212; current +0.00108 per
  step; angular flat 1.9124–1.9126 (`STAGE2_NEGATIVE_L_RECEIVER_LADDER_CLOSEOUT.md:40-60`).
  Dense mid vs outer (raw J): baseline 0.970928, mid 0.958663 (−1.26%), outer
  0.939090 (−3.28%) (`STAGE2_NEGATIVE_L_RECEIVER_PROMOTION_GATE.md:46-48`).
  At release width 1.00 only `gain1p0` beats the baseline in raw J (0.934785
  vs 0.944764); `p003_mid` gives 0.964451 (`STAGE2_NEGATIVE_L_RECEIVER_BETA100_RETIMING_LOCALITY.md:94-100`).
  *Algebraic type (later)*: receiver width ×{0.5, 1, 2} gives minimum
  discriminants −0.00422/−0.00206/−0.00125, Type IV at all three; narrowing
  raises the peak while ∫|Im λ| changes little (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:219-228`).
  *Curvature*: the mid profile's u^{1/2} factor makes a √ cusp at the inner
  edge; density −0.064 → −107.6 as the step falls 0.0025 → 1.95×10⁻⁵;
  setting only the receiver gain to 0 gives finite values
  (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:160-183`).
- (d) SWEEP.
- (e) DESIGN. **GEN-I pieces**: (i) spatially disjoint edits superpose
  exactly by locality of G_μν — bilateral J drop 0.016597 = 0.007128 +
  0.009469 and current +0.112518 = +0.110371 + 0.002147 (INVENTORY arithmetic
  on `STAGE2_BETA_MEMORY_RECEIVER_ANGULAR_SYMMETRY_MEMO.md:43-45`); (ii) J
  linear in small log gain (exp(g·w) ≈ 1 + g·w); (iii) a d^p cusp gives
  d^{p−2} stress (I13).
- (f) The receiver phase must match the release width: "the receiver should
  not be scaled by geometry alone. It should carry a phase/tail knob"
  (`STAGE2_NEGATIVE_L_RECEIVER_BETA100_RETIMING_LOCALITY.md:262-265`). The
  receiver dose lowers reset J but introduced the singular inner edge.
- (g) The two sides decouple exactly. Short memory underperforms: "the
  post-release memory tail is doing real work"
  (`STAGE2_NEGATIVE_L_RECEIVER_LADDER_CLOSEOUT.md:114-116`).
- (h) Orientation matters: +l costs 105% current, −l costs 2%, and the reports
  give no mechanism. INVENTORY INFERENCE: the packet centreline follows l = σ,
  so the +l flange overlaps the just-released carrier near l ≈ 1.5–1.9. The
  removed burden is booked almost entirely to the reset cap though the flange
  sits at the support edge. `mid` was promoted over `outer` on the one-sided
  transfer metric while `outer` had the larger raw J drop. The reset effect
  reverses sign between release widths 0.75 and 1.00.
- (i) **[β075]; `p003_mid` is the frozen geometry's receiver. Its √ cusp and
  outer slope jump are the singular-curvature finding, and the Type IV peak
  sits just outside its outer clip** (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:5-11, 185-189`) [L1].
  The May statement "There is no evidence here of a new curvature blow-up caused
  by the receiver" (`STAGE2_GZ_OBSTRUCTION_SCREEN.md:105`) is contradicted by that refinement.

#### G26. β-rematch collar: gain, shape, floor, width, temporal width, schedule

- (a) δβ = −g·W_r·(v + β), which drives the local shift toward the packet's
  coordinate velocity (`STAGE1_PACKET_BETA_REMATCH_TEMPORAL_PROBE.md:29`;
  `source_ledger.py:1522-1526`); shapes core/shoulder/annular/edge_soften/
  trailing_edge; centre floor joined by max, blend or add; spatial and temporal
  width multipliers; schedule live_only/catch_release/coordinated_release.
- (b) Gain 0.1–1.8; floor 0.45–0.65; width ×1.0–1.6 (Stage I); Stage II
  generator `rematch_w6_t1p5` vs `rematch_w8_t2p0` (gain 1.8, floor 0.6); local
  bracket w5.5/6.0/6.5 at t1.5 and t1.25 on dense beta075; mitigation edits
  (β smoothing, packet-β relaxation, areal smoothing, γ_ll smoothing).
- (c) Stage I: rematch gain alone at V5 lowers the point peak 7.60 → 6.56 at
  flat live null (`STAGE1_PACKET_BETA_REMATCH_TEMPORAL_PROBE.md:78-80`); at V10
  gain 0.6–1.0 restores safety while live null rises 0.120 → 0.157 (`:132-134`):
  "high beta rematch can restore V10 safety, but it restores radial-null burden
  too" (`:177`). Moving the collar off the pre-catch schedule gives 0 safe
  rows: "The beta floor is not merely a release cleanup term. At V5 it is also
  preserving live packet causal margin before catch/rematch"
  (`STAGE1_RELEASE_CHOREOGRAPHY_REFREEZE.md:100-105`). Blend vs max union at
  81×109: blend 1.6/1.0 safe with point peak 8.63; max 1.0/1.0 peak 117.2
  (`STAGE1_RELEASE_CHOREOGRAPHY_ARTIFACT_CHECK.md:113-120`). Stage II generator
  (`STAGE2_BETA_COLLAR_GENERATOR_SCREEN.md:74-168`):

| quantity | baseline | w6_t1p5 | w8_t2p0 |
|---|---:|---:|---:|
| caustic-like bundles | 8/8 | 0/8 | 0/8 |
| worst l-width ratio | 0.009603 | 0.275792 | 0.394689 |
| max live packet norm | – | −9.935129 | −6.577702 |
| live neg-T_kk ratio | 1 | 0.852 | 0.819 |
| live \|j_l\| ratio | 1 | 0.718 | 0.674 |
| live neg-ρ_packet | – | 0.000483 | 0.005930 |

  Local bracket w5.5 → w6.5: live neg-T_kk 12.163 → 11.867, live
  neg-ρ_packet 3.28×10⁻⁵ → 1.35×10⁻³, support-edge selected null 0.6381 →
  0.6463; temporal width "essentially neutral"
  (`STAGE2_BETA075_COLLAR_LOCAL_BRACKET_CHECKPOINT.md:29-74`; "essentially neutral", `:71`). Mitigation:
  β l-smoothing 0.45 widens the bundle 1.942×, packet-β relaxation 1.461×,
  areal smoothing 0.989×, γ_ll smoothing 0.354× (worse)
  (`STAGE2_COLLAR_MITIGATION_SCREEN.md:91-99`).
- (d) SWEEP + SINGLE.
- (e) **GEN-I**: the timelike margin gains algebraically,
  v+β → (1−gW)(v+β), best at gW = 1 (I7); radial bundle width responds to
  ∂_lβ and ∂_l(α/√A), never to B (I11), which the mitigation ranking
  confirms. Source-side effects DESIGN.
- (f) Collar width trades live relief against support-edge J and live
  packet-frame negative density (41× rise over the bracket); optical relief
  trades against packet-norm margin.
- (g) Live p_l is insensitive to rematch gain
  (`STAGE1_PACKET_BETA_REMATCH_TEMPORAL_PROBE.md:78-134`); reset-cap J is flat
  across the bracket.
- (h) The rematch is needed before the catch, not only at release. The wider
  collar places negative energy density inside the packet frame, an occupant
  WEC violation.
- (i) `rematch_w6_t1p5` is in the frozen geometry; 1,862 dense Type IV points
  sit on the rematch transition (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:89-90`)
  [β075][L1]. The collar's packet-norm success is built on the unit-speed
  window [L2].

#### G27. Causal-margin guard and local cone tilt

- (a) Clamp |β| to (1−m)α/√A inside a guard window (packet, edge or support),
  implementing "enforce a local margin such as `abs(beta) < alpha /
  sqrt(gamma_ll)`" (`STAGE2_GZ_OBSTRUCTION_SCREEN.md:143-144`;
  `source_ledger.py:1527-1546`).
- (b) Packet/edge/support guard on four release-width/receiver variants.
- (c) (`STAGE2_HORIZON_REACHABILITY_AND_CAUSAL_GUARD_REPORT.md:132-140`)

| guard | live branch-crossing edges | live g_σσ ≥ 0 points | min branch margin |
|---|---:|---:|---:|
| none | 53 | 133 | 0.008881 |
| packet | 31 | 87 | 0.024927 |
| edge | 30 | 86 | 0.006818 |
| support | 26 | 82 | 0.000029 |

  Every guarded case keeps a live g_σσ ≥ 0 region and fails the GZ screen;
  live packet norms stay negative (`:119-126`). About 39–42% of live samples
  have g_σσ ≥ 0 across ledgers (Stage II endpoint extraction). All radial
  seeds escape to the domain boundary (136/136, 1056/1056 at s12/s15)
  (`STAGE2_BETA_COLLAR_GENERATOR_SCREEN.md:127`; `STAGE2_SCHEDULED_ADM_CONFIDENCE_RUN.md:56-60`).
- (d) SWEEP. (e) Construction GEN-I (I5); effect DESIGN.
- (h) "it suppresses some discrete crossings while sharpening one local
  pinch" (`STAGE2_HORIZON_REACHABILITY_AND_CAUSAL_GUARD_REPORT.md:142-147`):
  fewer crossings can mean a thinner margin. By I5, g_σσ ≥ 0 marks an ergo-like
  region, not a horizon, and escape audits confirm rays leave it.
- (i) [β075]; [L4] escape means reaching either end of a two-ended space.
