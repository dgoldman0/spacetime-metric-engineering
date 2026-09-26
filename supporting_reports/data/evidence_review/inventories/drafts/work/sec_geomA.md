## 3. Geometry knobs

### 3.A Throat, standing plant and service load (May 16 – 20, with later transfers)

#### G1. Throat radius R_th (with support radius; compact vs wide)

- (a) Minimal areal radius of the throat. In this design the same parameter
  also sets the support-bump radius, and in the Stage I screen also R_Ω, the
  region masks and the shell band (§0.2). Project names: `Rth`,
  `support_radius`, `wide4_radius205`.
- (b) 1.75 vs 2.0 at V10, 41×61 (`POINT_LEVEL_FINDINGS.md:15-26`);
  1.75/1.90/2.05 on the compact wide4 base (`STAGE1_TOPOLOGY_SUPPORT_SCALING.md:60-66`);
  promoted pair `compact7_wide4_edge160` (1.75) vs `wide4_radius205` (2.05)
  (`STAGE2_COMPONENT_SOURCE_LEDGER_PROMOTED_PAIR.md:66-67`); 1.90/2.05 transferred
  to the repaired beta075 static slice (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:132-143`).
- (c) Responses:
  - *Demand magnitude, pointwise.* Live |p_l| peak 0.009531 → 0.007297 for
    1.75 → 2.0 (`POINT_LEVEL_FINDINGS.md:16, 22`): ratio 0.7656 = (1.75/2.0)²
    exactly. Radial-null point peak 1.039 → 0.878 → 0.751 for 1.75/1.90/2.05
    (`STAGE1_TOPOLOGY_SUPPORT_SCALING.md:62-64`), ratios 0.845 and 0.723
    against (1.75/R)² = 0.848 and 0.729 (INVENTORY arithmetic). Mean ρ of the
    infrastructure role A falls by 0.728 for 1.75 → 2.05 (identities extraction
    from `STAGE2_COMPONENT_ALGEBRA_PROMOTED_PAIR.md:39-41`).
  - *Demand magnitude, integrated.* Total neg-T_kk 458 → 558.9, total |p_l|
    69.12 → 83.04 (`POINT_LEVEL_FINDINGS.md:15-22`). Assigned infrastructure
    radial support 382.25 → 544.88 (+43%)
    (`STAGE2_COMPOSITE_SOURCE_ANSATZ_PROMOTED_PAIR.md:60-65`). On the repaired
    static slice over [−7,7]: negative-density integral +15.8%, negative
    radial-null +11.2%, |p_t| +27.4% (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:185-189`).
  - *Demand location.* Live |p_Ω| burden 1.245 → 1.435 → 1.651
    (`STAGE1_TOPOLOGY_SUPPORT_SCALING.md:62-64`); live p_Ω fraction 21.56% →
    28.28% (`STAGE2_FULL_GRID_SOURCE_DECOMPOSITION_ENTRY_GATE.md:114-115`);
    radial-null fractions fall (26.7% → 22.5%, `POINT_LEVEL_FINDINGS.md:15, 21`).
  - *Algebraic type.* Untested in every radius comparison.
  - *Packet norm.* Safe throughout; max live norm −22.82 → −23.40
    (topology run CSV [RUN-CSV], rows 2–4) [L2].
  - *Source supply ratio (longitudinal quantum gate).* Radius 1.90/2.05 lower
    the supplied fraction by 4.55%/8.45% at k/R₀²=0.01 on [−7,7]; optical
    length 15.780 → 16.233 and throat lapse 81.66 → 88.47
    (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:132-143, 177-181`). At
    k/R₀²=0.9 on [−3,3] the short-interval gate improves 1.18350 → 1.63076
    (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:164-170`).
- (d) SWEEP (3 values) + SINGLE comparisons across four contexts.
- (e) **GEN-I for the pointwise throat tension**: at a minimal sphere
  p_r = −1/(8πR₀²) independent of lapse and stretch (I17;
  `COUPLED_SOURCE_ROLE_AUDIT.md:104-107`). The exact (1.75/2)² ratio of the
  live p_l peak is this identity (INVENTORY match; the report does not state
  it). Throat-scale curvature stress falling ∝ R⁻² is dimensional. The
  integrated increases are DESIGN: the √A·B weight grows with R² and the
  R_th-scaled region masks grow too.
- (f) "radius broadening helps the non-live radial-null infrastructure peak
  while charging the live angular-pressure ledger" (`STAGE1_TOPOLOGY_SUPPORT_SCALING.md:94`);
  "R2.0 improves the radial-null and radial-pressure fractions, but by making a
  larger infrastructure ledger" (`POINT_LEVEL_FINDINGS.md:107`); "a smaller
  local peak can accompany a larger counted support requirement"
  (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:193-194`).
- (g) Not isolated: R_th moves the support bump with the throat, so packet
  norms change too. Combined with w_th = 0.75 at R 2.05 the mixed derivative
  score doubles (2.017×) while the peak stays low (`STAGE1_TOPOLOGY_SUPPORT_SCALING.md:70, 106`).
- (h) Peaks fall by the 1/R² law while every integrated measure rises; the
  compact reference was preferred on assigned burden
  (`GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md:32`).
- (i) [L4] this is the radius of a two-ended wormhole throat; [L1] type
  untested; [L6] for the September transfer; [L2] for packet norms.

#### G2. Support-edge width w_th ("radial softening") and the packet-norm cliff

- (a) Transition width of the support scalar W in the variable l². W sets
  the log-stretch, log-lapse, b and the shift (as W⁴) together.
- (b) 0.35 (shaped base) … 0.60 coarse (`RADIAL_PRESSURE_SOFTENING_FINDINGS.md:7, 58`);
  0.520–0.570 at 41×73 (`HIGHRES_BOUNDARY_REPORT.md:10-16`); 0.65, 0.75 on the
  wide4 base (`STAGE1_TOPOLOGY_SUPPORT_SCALING.md:49`); ×{0.5,1,2} on frozen
  beta075 (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:209-214`).
- (c) Responses (41×73, V10, η_N=1; `HIGHRES_BOUNDARY_REPORT.md:10-16, 66-72`):

| w_th | live p_l ratio | live T_kk ratio | T_kk peak ratio | max live packet norm |
|---|---:|---:|---:|---:|
| 0.35 | 1 | 1 | 1 | −467.882 |
| 0.520 | 0.8525 | 0.8018 | 0.954 | −258.474 |
| 0.540 | 0.8320 | 0.7736 | 0.943 | +4276.14 |
| 0.565 | 0.8061 | 0.7384 | 0.929 | +15119.3 |
| 0.569 | 0.8020 | 0.7327 | 0.926 | +16714.1 |
| 0.570 | 0.8010 | 0.7313 | 0.926 | +17106.8 (2 pts) |

  - *Magnitude.* Total p_l 69.1145 → 51.0469 and total T_kk 424.4 → 286.709:
    widening reduces demand globally (`HIGHRES_BOUNDARY_REPORT.md:10-16`). The
    live |p_l| **point peak** is the same for every w_th (pre-stage extraction;
    same table); it equals the throat tension 1/(8πB(0)) ≈ 0.00953 with the
    jacket's c_Ω (INVENTORY DERIVATION).
  - *Location.* Live fractions rise slightly (p_l 0.2495 → 0.2706) while
    absolute live burdens fall.
  - *Packet norm / cliff.* With the lapse cushion at η_N = 2 (G3): 0.569 safe
    (−198.925), 0.570 unsafe (+228.109) at V10 (`ROBUSTNESS_FINDINGS.md:27, 38`).
    "The `w_th = 0.570` cliff is not a universal cliff at lower V. It is safe
    at `V = 2` and `V = 5`, unsafe at `V = 10`" (`V_SWEEP_FINDINGS.md:83`).
    Failing nodes: (σ,l) = (−0.35, −0.7) for raw widening and (−0.35, 0) for
    0.570, both on the first sampled time row (`HIGHRES_BOUNDARY_REPORT.md:66-72`).
  - *V headroom.* Shaped base (w_th 0.35) stays safe to V ≈ 12.0; tuned 0.569
    only to 10.00 (`V_SWEEP_FINDINGS.md:62-75`): "radial softening and lapse
    cushioning improved source burden but spent a lot of V headroom" (`:85`).
  - *Algebraic type (frozen beta075, repaired classifier).* Widening worsens
    Type IV: w_th × {0.5, 1, 2} give minimum discriminants −0.001403,
    −0.002064, −0.002272 and ∫|Im λ| 0.06619, 0.07617, 0.09026
    (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:211-214`).
  - Wider still (0.65, 0.75) on wide4: live T_kk burden falls 8.83 → 8.01 while
    the mixed derivative score rises ~56% and the max point peak rises 1.04 →
    1.98 ([RUN-CSV] rows 2, 5, 6; `STAGE1_TOPOLOGY_SUPPORT_SCALING.md:67-68, 96-101`).
- (d) SWEEP.
- (e) DESIGN. INVENTORY INFERENCE (pre-stage extraction): the p_l burden
  reduction tracks the shortened proper radial length √A inside the packet
  window (√A ratio ≈0.74–0.81 against burden ratio 0.802), not a lower local
  stress; with an invariant p_l peak this is consistent with I17.
- (f) "Tkk wants shaped catch timing. p_l wants radial support-edge widening.
  packet safety sets a hard upper bound on w_th" (`RADIAL_PRESSURE_BOUNDARY_FINDINGS.md:58-60`).
- (g) w_th and R_th are the only pre-stage knobs that move p_l; w_th moves p_l
  and T_kk together.
- (h) Resolution reversed the verdict: "The previously reported safety cliff
  was therefore under-resolved and moved substantially downward"
  (`HIGHRES_BOUNDARY_REPORT.md:129`). INVENTORY INFERENCE (pre-stage
  extraction, section E): both cliffs are the sign flip of a single
  packet-mask-edge node (S = ½) on the first sampled row; a closed-form
  estimate of v_rel = √A|v+β|/α at (−0.35, 0) reproduces the 12.0/12.1 base
  cliff and the 10.00/10.01 tuned cliff, and predicts the η_N sensitivity
  (1.82 per 0.2 in η_N) that is measured as 1.817 and 1.818
  (`ROBUSTNESS_FINDINGS.md:24, 27, 29`). The same estimate at unsampled
  earlier catch times (σ ≈ −0.45 to −0.64) gives v_rel ≈ 1.05–1.07 for the
  tuned design at V10, i.e. a packet failure outside the sampled domain
  (unverified).
- (i) [L2] governs the cliff; [L1] (w_th shapes the transition hosting 3,764
  Type IV points); the cliff values are properties of where the mask edge was
  sampled.

#### G3. Lapse cushion η_N

- (a) Gaussian log-lapse shoulder: α ∝ exp(0.18 η_N q e^{−((|l|−1.05)/0.35)²})
  (`source_ledger.py:1462-1463`). Raises local light speed α/√A in a band
  around |l| = 1.05.
- (b) 1.0, 1.2, 1.5, 1.8, 2.0, 2.2.
- (c) *Packet norm*: raw widening that failed becomes safe — w_th 0.54 at
  η 1.2 (−249.3), 0.55 at 1.5 (−250.5), 0.565 at 2.0 (−254.0), 0.569 at 2.0
  (−198.9); 0.570 at 2.0 stays unsafe (+228.1), 0.580 fails (+4423)
  (`COMPENSATOR_HIGHRES_REPORT.md:24-38`). η 1.8/2.0/2.2 at w_th 0.569:
  −197.108/−198.925/−200.743 (`ROBUSTNESS_FINDINGS.md:24, 27, 29`). V
  headroom unchanged: tuned_eta220 10.00/10.01 (`V_SWEEP_FINDINGS.md:65`).
  *Radial pressure*: unchanged — "increasing `eta_N` barely changes the live
  `p_l` burden at a fixed `w_th` … The lapse cushion is therefore a safety
  compensator, not the source-reduction knob itself"
  (`COMPENSATOR_HIGHRES_REPORT.md:56`). *Radial null*: live burden rises
  slightly (0.7384 → 0.7418 at w 0.565), peak falls (0.9287 → 0.8984)
  (`COMPENSATOR_HIGHRES_REPORT.md:32-35`).
- (d) SWEEP.
- (e) **Sign GEN-I**: ∂(−α² + A(v+β)²)/∂α = −2α < 0, so raising α makes every
  carried worldline more timelike (I6). Everything else DESIGN.
- (f) Enables wider w_th. INVENTORY INFERENCE: the shoulder weight at l = 0 is
  e⁻⁹, so the cushion cannot protect the throat-centre node that sets the
  0.570 and V ≈ 10.01 cliffs; "more cushion does not reopen much room beyond
  the old w_th ≈ 0.569 boundary" (`ROBUSTNESS_FINDINGS.md:18`).
- (g) **Decoupling result**: η_N moves packet safety at fixed p_l.
- (h) Part of any lapse effect on the coordinate T_kk channel is α²
  normalization (I8).
- (i) [L2]; [L1]. Its |l| kink at the origin gives an h⁻¹ angular-pressure
  surface term later repaired (G28).

#### G4. Angular capacity jacket (width w_Ω; transferred width 1.80/2.20)

- (a) Radial width of the time-dependent R-widening factor c_Ω.
- (b) w_Ω 1.40/1.80/2.20 (`STAGE1_TOPOLOGY_SUPPORT_SCALING.md:50, 62-66`); the
  jacket amplitude a_Ω = 0.20 was never varied.
- (c) Live |p_Ω| 1.245 → 1.221 → 1.205; T_kk peak 1.039 → 1.051 → 1.063;
  packet norm identical ("nearly neutral for the radial-null mixed score",
  `:104`). Transferred to repaired beta075: supply ratio −0.117%/−0.194%
  (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:138-139`).
- (d) SWEEP. (e) DESIGN.
- (g) Largely decoupled from packet norm and radial null.
- (i) The jacket's time dependence is one of three sources of R variation on
  which decompression generates Type IV (`CONSTANT_RADIUS_TRACK.md:68-71`) [L1].

#### G5. Support decompression schedule (the "reset") and uniform slowdown

- (a) The time profile q(σ) that relaxes the standing stretch and support
  lapse; and a uniform reparametrization σ = κt of the whole service
  (`LE_BOUNDED_METRIC_REPAIR.md:101-110`).
- (b) Attribution toggles on repaired beta075 (`CONSTANT_RADIUS_TRACK.md:55-65`);
  κ = 1 … 1/64 at 28 roots × 3 resolutions (`LE_BOUNDED_METRIC_REPAIR.md:150-192`);
  decompression schedule on the constant-R track (post-era,
  `CONSTANT_RADIUS_TRACK.md:297-315`).
- (c) *Algebraic type*: attribution (grid 0.1):

| control | Type IV points | ∫\|Im λ\| |
|---|---:|---:|
| repaired beta075 | 842 | 3.37×10⁻² |
| decompression alone | 874 | 3.58×10⁻² |
| decompression removed | 252 | 6.69×10⁻⁴ |
| static support, moving packet windows, zero shift | 236 | 8.06×10⁻⁴ |
| static support with carrying flow, no windows | 19 | 2.01×10⁻⁷ |

  Slowdown: "At rates from 1/4 through 1/64, all 28 root locations have Type IV
  demand at every resolution" (`LE_BOUNDED_METRIC_REPAIR.md:153-154`); at the
  reset root Δ = −1.2757×10⁻⁴ (κ=1) → −7.72×10⁻⁸ (κ=1/64), |Im λ| 0.005647 →
  0.000139, layer width ≈0.00556 → 0.00272 (`:173-192`); on the ordinary
  0.025 grid the slow cases look all Type I (`:187-192`).
  *Angular NEC on a constant-R track (post-era)*: integrated angular deficit
  0.373 (current) → 0.311 (after live window) → 0.118 (half rate) → 0.0063
  (quarter rate) → 0.0037 (removed); all points Type I
  (`CONSTANT_RADIUS_TRACK.md:297-303`). *Service*: packet-coordinate proxy
  1.2368 → 1.1989 [L3] (`:313-315`). *Endpoint J*: release lapse lag and
  carve lag 0 → 0.25 leave J unchanged to 6 digits
  (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:185-202`).
- (d) SWEEP + DERIVATION (I9).
- (e) **GEN-I**: (i) by I2+I3, time dependence acting where R varies separates
  the radial null energies — the attribution confirms decompression is the
  dominant Type IV generator; (ii) by I9, uniform slowdown cannot remove Type IV
  at an enthalpy zero with nonzero current (|Δ| ∝ κ², width ∝ κ). Magnitudes
  DESIGN.
- (f) Slower decompression thins the layer and lengthens the service.
- (g) Lapse-only and carve-only retiming are decoupled from endpoint J.
- (h) "the static limit can be Type I while every nearby evolving member still
  contains Type IV stress" (`LE_BOUNDED_METRIC_REPAIR.md:134-136`); coarse grids
  hide the thin layer.
- (i) The design rule that follows is G31 (hold R constant where the metric
  evolves). The "relax throat" reading is invalid: the minimal sphere persists
  [L4].

#### G6. Service factor V (carry-speed load)

- (a) U = v_exit + (V − v_exit)·catch; scales β and the packet speed v = U/b.
  V5 is the operating reference, V10 the "recognized edge" (PDF p.1).
- (b) V = 2, 5, 10, 11–15 (`V_SWEEP_FINDINGS.md:14-32`), fine scan 10.00–10.21
  and coarse 10–15 (`:58-75`); V2/V5/V8/V10 across Stage I branches; V2, 2.5, 5,
  10 on dense beta075 (`STAGE2_BETA075_SERVICE_RATING_LADDER_DIAGNOSTIC.md`;
  `STAGE2_BETA075_V2_LOWER_SERVICE_SOURCE_COUPLING.md`).
- (c) Responses:
  - *Radial null (tuned design, live burden)*: 42.21 (V2), 52.06 (V5), 72.38
    (V10), 96.76 (V15); live fraction 0.150 → 0.178 → 0.228 → 0.280; point
    peak 0.1001 (V2, V5) → 0.1427 (V10) → 0.2044 (V15)
    (`V_SWEEP_FINDINGS.md:18-32`). V pushes null demand into the packet.
  - *Radial pressure*: live |p_l| 13.8318–13.8319 for V = 2–15; point peak
    0.0115534 at every V (`V_SWEEP_FINDINGS.md:14-32`): "The radial pressure
    burden is essentially fixed by the standing support geometry"
    (PDF p.3). Stage I: p_l, p_Ω, j_l totals unchanged V5 → V10 on the shell
    candidate (87.356; 3.923 → 3.928; 0.2643 → 0.2644)
    (`STAGE1_V5_MINIMAL_TRAVERSABILITY_SCREEN.md:87-92`; `STAGE1_V10_SELECTED_CANDIDATE_EDGE_CHECK.md:75-80`).
  - *Non-live core null peak*: identical at V2 and V5, 1.289256
    (`STAGE1_SPLIT_CARVE_NULL_CUSHION_PROGRESS.md:132, 201`).
  - *Shift response (ADM)*: live Δj_l fraction 0.1175 → 0.1925, "about 1.79×"
    from V5 to V10; "The live service signal is ∆jl , not ∆ρ" (PDF p.4-5).
  - *Packet norm*: tuned max live norm −251.3 (V2, V5) → −198.9 (V10) →
    +42,605 (V11) … +254,483 (V15); last safe V 10.00, first unsafe 10.01
    (`V_SWEEP_FINDINGS.md:38-66`). Beta075 dense: −6.3337225 identical to 16
    digits at V2, V2.5, V5; +1135.50 with 123/966 positive live points at V10
    (`STAGE2_BETA075_SERVICE_RATING_LADDER_DIAGNOSTIC.md:213-218`;
    `STAGE2_BETA075_V2_LOWER_SERVICE_SOURCE_COUPLING.md:50-52`).
  - *Source model (beta075)*: total demand nearly flat V2 → V5 (neg-T_kk
    480.68 vs 476.99) while live fraction rises 0.0165 → 0.0251 and the
    support-edge source-coupling budget rises 0.616 → 2.076
    (`STAGE2_BETA075_V2_LOWER_SERVICE_SOURCE_COUPLING.md:41-46, 84-94`).
    Constrained field closure is non-monotone: pass V2 (0.0123), fail V2.5
    (0.17851321), pass V5 (0.0095), fail V10 (0.17851277)
    (`STAGE2_BETA075_SERVICE_RATING_LADDER_DIAGNOSTIC.md:82-84, 259-261`).
- (d) SWEEP across four branches.
- (e) DESIGN magnitudes. **GEN-I structure**: from the ADM constraints
  (PDF p.2 eqs. (9)–(14)), at fixed (α, A, B) j_l is affine in β with a 1/α
  prefactor and Δρ quadratic with 1/α² (pre-stage extraction C17, INVENTORY
  DERIVATION); where B′ = Ḃ = 0 a shift produces no j_l at all. The V-independence
  of p_l is consistent with I17 (throat tension depends on R only) and with the
  1/α suppression of shift terms (α ≈ 450 at the throat).
- (f) V consumes packet margin first; softening/cushioning spends V headroom
  (G2, G3). Restoring V8/V10 safety by β rematch "again raises live radial-null
  burden" (`STAGE1_PACKET_BETA_REMATCH_TEMPORAL_PROBE.md:167, 203`).
- (g) **Decoupling**: V moves radial null and packet norm; p_l, total j_l, total
  p_Ω and the non-live core null peak are V-independent.
- (h) Lowering V does not reach the strict live-fraction criterion: "The strict
  packet/source-separation criterion still fails even at V2"
  (`STAGE1_V2_LOW_SERVICE_GATE_MEMO.md:80`). The beta075 V2.5 and V10 closure
  errors agree to 6 digits, unexplained.
- (i) [L2] for every cliff; [L3] if V is read as service speed; [L1] for
  closure/source results; the G2 cliff reconstruction applies to the V ≈ 10.01
  cliff.

#### G7. Catch/rematch shaping: one-component shaping vs two-component split

- (a) Timing, width and profile of the two catch schedules (support-side shift
  catch c_β and packet rematch c_packet), and their lead
  (`BIFURCATION_INTERIM_DECISION.md:1-14`). Side knobs: packet-window edge
  width w_pass; a localized lapse "shock absorber" at the inner packet edge.
- (b) Shaping (`shape_early_minjerk_w32`) vs spatial splits (`broad100`,
  `broad75`) vs temporal split (`split_temporal_beta_early`), 25×41
  (`BIFURCATION_INTERIM_DECISION.md:32-36`); locked lead 0.05 with w 0.32
  (`SHAPED_CATCH_CANDIDATE_NOTE.md:31-59`); earlier/later/softer on the tuned
  design (`ROBUSTNESS_FINDINGS.md:25-26, 40`); w_pass 0.055/0.06/0.08; shock
  absorber amplitude 0.15–0.80 (`SHOCK_ABSORBER_FINDINGS.md:36-41`).
- (c) Fork outcome:

| case | live T_kk vs base | live p_l vs base | T_kk peak vs base | packet failure |
|---|---:|---:|---:|---|
| temporal split | 0.816 | 1.000 | 0.983 | yes |
| early min-jerk shaping | 0.859 | 1.000 | 0.999 | no |
| spatial broad100 | 0.930 | 1.000 | 1.423 | no |
| spatial broad75 | 0.933 | 1.000 | 1.180 | no |

  Shaping moves null burden between stages: entry 61.53 → 0.00, catch 66.67 →
  116.59, release 17.95 → 8.94 (`BIFURCATION_INTERIM_DECISION.md:47-55`). On
  the tuned design, a later locked lead fails the packet norm (+2169.02)
  while earlier/softer variants stay safe (`ROBUSTNESS_FINDINGS.md:25-26, 40`).
  w_pass 0.06 → 0.08 lowers the T_kk peak 0.9081 → 0.7607 at fixed p_l
  (`RADIAL_PRESSURE_SOFTENING_FINDINGS.md:29-30`). Shock absorber: live catch
  T_kk 0.983/0.978/0.972 with global peak 1.024/1.042/1.113; amplitude 0.80
  gives 1.002 and peak 1.843 (`SHOCK_ABSORBER_FINDINGS.md:36-41`).
- (d) SWEEP (small).
- (e) DESIGN. **Mechanism GEN-I**: inside the packet v + β = (U_p −
  U_β E W⁴ S)/b, so any lag between shift and packet schedules enters the
  timelike test directly (I6; pre-stage extraction). "the system wants
  beta/support catch to happen earlier, but packet-frame rematch cannot be left
  behind" (`BIFURCATION_INTERIM_DECISION.md:38`).
- (f) Catch timing trades radial NEC exposure against packet safety.
- (g) **Decoupling**: "negative radial-null exposure = mostly catch shaping /
  timing; radial pressure exposure = likely a separate radial-geometry/support-
  channel issue" (`BIFURCATION_INTERIM_DECISION.md:100-101`); p_l = 1.000 in
  every catch, w_pass and shock-absorber case.
- (h) The strongest null reducer (temporal split) breaks the packet handoff;
  spatial splits lower fractions by "mostly moving denominators and peak
  locations" (`BIFURCATION_INTERIM_DECISION.md:26`); a strong lapse guard is
  counterproductive (`SHOCK_ABSORBER_FINDINGS.md:45`).
- (i) [L2] — the packet norm is exactly the mismatch readout; sampling of the
  entry stage differs across grids (§0.5); [L1].

**Knob-separation summary for the pre-stage design** (`FREEZE_REPORT.md:40-43`;
`ROBUSTNESS_FINDINGS.md:86-89`): radial null ← catch timing; radial pressure ←
w_th and R_th; packet safety ← lapse cushion; V headroom ← a sharp cliff. The
p_l separation is explained by I17 (INVENTORY match); the others are measured.
