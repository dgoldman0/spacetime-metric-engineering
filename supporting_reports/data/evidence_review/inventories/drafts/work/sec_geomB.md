### 3.B Packet-local containment knobs (Stage I, May 17 – 20)

All results in 3.B are measured on one design family at V5 or V10 on grids of
31×55 to 81×109. Absolute burdens change with grid and domain: the same
wide4 case gives live T_kk burden 8.83 (41×61), 8.50 (61×83) and 15.94
(extended domain) ([RUN-CSV] row 2;
`STAGE1_COMPACT_HANDOFF_HIGHRES_FINDINGS.md:53`; `STAGE1_COMPACT_ENTRY_STAGE_SCREEN.md:68`).
No report in 3.B computes a Hawking–Ellis type, DEC, SEC, tangential NEC or an
occupant tide/acceleration; the radial-NEC channel is the coordinate
quantity of I8. Every packet-norm number carries [L2]; every source ranking
is blind to the Type IV content later found in this lineage [L1].

**Design-family causal-headroom relation (INVENTORY DERIVATION from
`source_ledger.py:1459-1466, 1497, 1515, 1550`).** With overlays off, the
support scalar W drives lapse (λC₀)^{qW}, stretch √A = B·C₀^{qW} and shift
∝ W⁴/B together; C₀ and B cancel and the packet is timelike iff
√f_r·|U_p − U_β E W⁴ S| < f_α·n_cushion·λ^{qW} (f_r, f_α the local γ_ll and α
factors). Without shift the condition is U < n·λ^{qW}. Carving W removes
headroom, positive γ_ll gain divides it by e^{g/2}, lapse gain multiplies it
by e^{g}. This is the algebraic core of the three-way trade (live exposure,
causal margin, point peak) that the Stage I reports rediscover repeatedly
(`STAGE1_V2_LOW_SERVICE_GATE_MEMO.md:83-89`). It is specific to the tied-field
construction; the class-level content is I6.

#### G8. Packet carve (exclusion of support under the occupant tube)

- (a) W → W_raw(1 − c·window(|l−s|)): locally removes the prepared stretch,
  lapse and carrying shift under the occupant worldtube
  (`STAGE1_PACKET_CARVE_HARNESS_AND_SWEEP.md:14, 35-44`).
  Project name `standing_support_packet_exclusion`.
- (b) V5: 0–0.24; V10: 0–0.16 (`STAGE1_PACKET_CARVE_HARNESS_AND_SWEEP.md:113, 159-164`);
  later 0.32, 0.60, 0.70, 0.90.
- (c) V5 (`STAGE1_PACKET_CARVE_HARNESS_AND_SWEEP.md:118-124`):

| carve | packet failures | live T_kk fraction | live p_l fraction | max total ratio |
|---:|---:|---:|---:|---:|
| 0.00 | 0 | 0.221837 | 0.261006 | 1.054489 |
| 0.12 | 0 | 0.107606 | 0.169186 | 1.070796 |
| 0.16 | 0 | 0.087072 | 0.144818 | 1.079520 |
| 0.20 | 0 | 0.072283 | 0.123389 | 1.089866 |
| 0.24 | 1 | 0.061485 | 0.104700 | 1.102152 |

  V10 failures 3 → 11 → 20 → 80 → 135 → 162 for carve 0 → 0.16
  (`:157-164`): "carving improves source placement but consumes causal margin"
  (`:166`). Demand location: top hard points move from packet_in_support to
  core_throat (`STAGE1_TWO_ZONE_PACKET_CARVE_SWEEP.md:97`). Weaker carve on
  the May 18 candidate (0.90 → 0.70) raised packet margin ~9× and cut
  angular/current peaks (p_Ω ×0.152, j_l ×0.317) while raising live null
  burden ×1.353 and live p_l ×2.087
  (`STAGE1_CURRENT_CANDIDATE_ALGEBRA_LEDGER.md:289-297`).
- (d) SWEEP. (e) Measured on this design; the causal cost follows from the
  tied-field relation above.
- (f) Live exposure against total burden and causal margin.
- (g) **Live p_l fraction is fixed by the carve footprint alone**, to 5–6
  digits across V and lapse settings: 0.169186 (V5) / 0.169187 (V10) /
  0.169190 (V5 and V10 with lapse gain 0.75)
  (`STAGE1_PACKET_CARVE_HARNESS_AND_SWEEP.md:121, 163`;
  `STAGE1_CARVE_LAPSE_COMPENSATOR_SWEEP.md:94, 129`). The live T_kk fraction
  does depend on V (0.2218 V5, 0.3073 V10). No report explains the invariance.
- (h) Total burden rises while live exposure falls.
- (i) [L1] carve edits the decompressing plant that alone produces Type IV
  (`CONSTANT_RADIUS_TRACK.md:59-68`); [L2].

#### G9. Packet lapse compensator: gain and footprint

- (a) α → α·exp(g·window), α only. Co-located (same window as the carve,
  `STAGE1_CARVE_LAPSE_COMPENSATOR_SWEEP.md:7-9`) or decoupled (independent
  radius r and width w multipliers, `STAGE1_DECOUPLED_CARVE_LAPSE_COMPENSATOR_SWEEP.md:18-26`).
- (b) Co-located g 0–0.30 (V5), up to 0.75 (V10). Decoupled at V10: carve
  0.12–0.16, g 0.55–0.75, r 1.1–1.4, w 0.5–2.5 (108 cases).
- (c) Co-located at V10 (carve 0.12, g 0.75): 0 failures (135 without lapse),
  live T_kk 0.2825; the same setting at V5 raises live T_kk to 0.2516, above
  the uncarved 0.2218 (`STAGE1_CARVE_LAPSE_COMPENSATOR_SWEEP.md:94, 126-129`):
  "packet-local lapse can buy back causal margin, but it partially
  reintroduces radial-null burden" (`:158`). Decoupled: 103 of 108 safe;
  best carve 0.16 / g 0.55 / r 1.4 / w 1.2 gives live T_kk 0.1597 at V10;
  w ≥ 2.0 fails the V10 packet gate
  (`STAGE1_DECOUPLED_CARVE_LAPSE_COMPENSATOR_SWEEP.md:82-96`). V5 back-check
  point-peak ratio 2.08 (`:122`).
- (d) SWEEP. (e) Measured.
- (g) **Partial decoupling.** Lapse leaves the live p_l fraction unchanged
  (G8g). It does not separate from T_kk: moving the lapse gradient out of the
  tube (r 1.4, w 1.2–1.6) cut V10 live T_kk from 0.2825 to 0.1596 at equal
  safety. The footprint of the lapse gradient, more than its gain, sets how
  much null burden returns to the tube.
- (h) Part of the lapse effect on the T_kk channel is the α² normalization of
  I8; the reports never separate it.
- (i) [L2]; superseded by G10.

#### G10. Carve shoulder: filled two-zone vs annular

- (a) A second carve zone around the core, either filled (clip(core+shoulder))
  or an annulus (outer minus inner window)
  (`STAGE1_TWO_ZONE_PACKET_CARVE_SWEEP.md:15-19`; `STAGE1_ANNULAR_SHOULDER_SHAPING_PROBE.md:17-21`).
- (b) Two-zone: core 0.17, shoulder 0.05. Annular moderate: core 0.32,
  annulus 0.08; deep: core 0.60, annulus 0.12.
- (c) Two-zone vs decoupled lapse: V10 live T_kk 0.1596 → 0.1295, live p_l
  0.1448 → 0.1143, safe at V5 and V10 (`STAGE1_TWO_ZONE_PACKET_CARVE_SWEEP.md:90-95`).
  Annular (`STAGE1_ANNULAR_SHOULDER_SHAPING_PROBE.md:67-96`):

| case | failures | live T_kk | live p_l | point-peak ratio |
|---|---:|---:|---:|---:|
| moderate V5 | 0 | 0.0965 | 0.0754 | 7.60 |
| moderate V10 | 0 | 0.0957 | 0.0754 | 4.10 |
| deep V5 | 0 | 0.0572 | 0.0237 | 11.10 |
| deep V10 | 165 | 0.0419 | 0.0235 | 6.14 |

- (d) SWEEP. (e) Measured.
- (g) Radial pressure yields to carving more readily than radial null:
  "Radial pressure can be pushed much lower, but radial-null exposure stalls
  unless the metric pays with V10 causal-margin failure and large peaks"
  (`STAGE1_ANNULAR_SHOULDER_SHAPING_PROBE.md:112`).
- (h) "The rising V5 point peaks suggest that the transition geometry is now
  the limiting design problem" (`STAGE1_TWO_ZONE_PACKET_CARVE_SWEEP.md:120`).
- (i) [L2]. Deep branch is "a diagnostic boundary, not a selected architecture"
  (`STAGE1_ANNULAR_SHOULDER_SHAPING_PROBE.md:129`).

#### G11. Split carve, null cushion, smooth-split composition and edge sleeve

- (a) Entry and catch carves on separate schedules; a weak negative α gain on
  an annulus during catch ("null cushion"); a composition rule for
  overlapping carve pieces (`smooth_union` 1−Π(1−v_i) vs `additive` clip(Σv_i));
  an annular edge sleeve carve (`STAGE1_SPLIT_CARVE_NULL_CUSHION_PROGRESS.md:19-56`;
  `STAGE1_SMOOTH_SPLIT_ANSATZ_PROGRESS.md:22-67`; `source_ledger.py:633-646`).
- (b) Split: entry 0.75 / catch 0.15 vs single 0.90. Cushion −0.03, −0.05,
  −0.07. Edge sleeve 0–0.08.
- (c) Split vs single (V5, 81×109): live j_l 0.119 → 0.0655, live p_Ω 2.747 →
  1.952, p_Ω peak 0.5705 → 0.2202, T_kk peak 1.289 → 1.068; live T_kk burden
  9.714 → 10.017; margin −5.455 → −23.767
  (`STAGE1_SPLIT_CARVE_NULL_CUSHION_PROGRESS.md:124-147`). Cushion −0.03 →
  −0.07: live T_kk 9.626 → 9.546, p_Ω 1.949 → 1.928, p_l and j_l up by
  ~0.05%, slight margin loss (`STAGE1_SMOOTH_SPLIT_ANSATZ_PROGRESS.md:225-248`).
  Edge sleeve 0 → 0.08: live T_kk 9.977 → 9.228 and p_l 0.4013 → 0.3790 down,
  j_l 0.0659 → 0.0684 and p_Ω 1.908 → 1.979 up, monotone
  (`STAGE1_SMOOTH_SPLIT_ANSATZ_PROGRESS.md:159-211`).
- (d) SWEEP and single comparisons. (e) Measured.
- (f) Radial (null, pressure) against angular/current, monotone and
  sign-coherent.
- (h) `smooth_union` "removed useful overlap between the entry/catch/shoulder
  pieces and raised the integrated live radial burden"
  (`STAGE1_SMOOTH_SPLIT_ANSATZ_PROGRESS.md:67`): superposition of pieces
  matters, the envelope alone does not decide the demand. A wiring bug first
  made `additive` look worse (`:86-90`).
- (i) This smooth-split lineage becomes the frozen beta075 geometry with the
  Type IV layer (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:21`) [L1]; [L2].

#### G12. Coupled edge carve and pressure rebate

- (a) Edge carve plus a "rebate" that restores W in the same annulus:
  carve = raw − min(raw, rebate·edge_window) (`source_ledger.py:1447-1455`).
- (b) Edge 0.18/0.24; rebate 0, 25%, 50% (31×55).
- (c) (`STAGE1_COUPLED_PROFILE_PRESSURE_REBATE_FINDINGS.md:116-170`)

| case | live T_kk | live p_l | T_kk peak |
|---|---:|---:|---:|
| current | 10.150 | 0.410 | 1.228 |
| edge 0.24, no rebate | 11.284 | 0.610 | 0.822 |
| edge 0.24, rebate 25% | 16.39 | 0.816 | 0.963 |
| edge 0.24, rebate 50% | 24.97 | 1.119 | 4.193 |

  Edge carve alone cut live p_Ω 2.669 → 0.908 and live j_l 0.1235 → 0.0390.
- (d) SWEEP (5 cases). (e) Measured.
- (h) Restoring support mass made every radial channel worse: "The next law
  should preserve derivative/cancellation structure, not local support mass"
  (`STAGE1_COUPLED_PROFILE_PRESSURE_REBATE_FINDINGS.md:224`).

#### G13. Local radial stretch profile on A (core, catch ring, outer skirt)

- (a) γ_ll *= exp(core·w_core + ring·w_ring + skirt·w_skirt): local
  proper-length shaping around the packet, A only
  (`STAGE1_TWO_FEATURE_RADIAL_PROFILE_PROBE.md:33-38`;
  `STAGE1_REFINED_RADIAL_SUPPORT_LAW_PROGRESS.md:38-42`).
- (b) Sign ±; core 0.05/0.06; ring 0.08/0.12; ring radius 2.0–2.4 × width
  2.4–3.2; skirt +0.05.
- (c) "negative radial softening was not the right direction; positive radial
  stretch was the useful direction" (`STAGE1_REFINED_RADIAL_SUPPORT_LAW_PROGRESS.md:92-93`).
  2.4/2.4 ring vs base: live T_kk fraction −0.000174, p_l +0.000067, j_l
  −0.000305, p_Ω −0.00800; T_kk peak ×0.961, p_Ω peak ×0.943
  (`STAGE1_RADIAL_SUPPORT_GEOMETRY_REFINEMENT.md:106-114`). Skirt: changes of
  order 1e−7 to 1e−5, "fine-trim scale"
  (`STAGE1_TWO_FEATURE_RADIAL_PROFILE_PROBE.md:170-181, 197`).
- (d) SWEEP. (e) Measured. Effects (≤2.6% relative) are smaller than the
  grid sensitivity documented above.
- (g) **The core sets the peaks; the ring moves only live fractions.** Identical
  T_kk peak 1.285178196 and packet norm −21.612436 across ring gains 0.08/0.12
  and three ring geometries (`STAGE1_REFINED_RADIAL_SUPPORT_LAW_PROGRESS.md:140, 150`;
  `STAGE1_RADIAL_SUPPORT_GEOMETRY_REFINEMENT.md:80-101`).
- (f) Narrow ring: better T_kk/p_Ω, worse p_l/j_l; wide ring the reverse
  (`STAGE1_RADIAL_SUPPORT_GEOMETRY_REFINEMENT.md:137-144`).
- (i) Retained in the September construction manifest
  (`GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md:118-121`); transferred to repaired
  beta075, core gain 0.04/0.06 changed the longitudinal supply ratio by
  −0.314%/+0.315%, ring/skirt by <0.06%
  (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:132-143`).

#### G14. Local areal-radius partner (smooth-split angular log gain)

- (a) γ_Ω *= exp(g·window) on the edge footprint: the only Stage I packet
  knob that edits R (`STAGE1_SMOOTH_SPLIT_PAIRED_COMPENSATOR_RESULTS.md:13-21`).
- (b) g = −0.20 … +0.20 (8 values, 41×61).
- (c) (`STAGE1_SMOOTH_SPLIT_PAIRED_COMPENSATOR_RESULTS.md:53-66`)

| g | live T_kk | live p_l | live j_l | live p_Ω | T_kk peak |
|---:|---:|---:|---:|---:|---:|
| −0.20 | 30.750 | 0.4317 | 0.0654 | 1.884 | 5.643 |
| −0.025 | 11.447 | – | – | – | 1.147 |
| 0 | 9.745 | 0.3971 | 0.0682 | 1.957 | 0.958 |
| +0.10 | 8.417 | – | – | – | – |
| +0.20 | 8.864 | 0.3715 | 0.0983 | 2.035 | 1.232 |

- (d) SWEEP. (e) Numbers measured. **Direction identity-backed**: by I2 a local
  dip in R (negative g) makes R convex along null rays and costs radial null
  energy; a bump relieves it until its own flanks turn convex (non-monotone
  at +0.20). The report does not make this connection.
- (f)/(g) "the local `gamma_omega` factor can move cost between the radial-null
  side and the current/angular side … It does not provide an independent
  cancellation direction" (`STAGE1_SMOOTH_SPLIT_PAIRED_COMPENSATOR_RESULTS.md:96`).
- (h) A −0.025 trim erases the whole smooth-split radial gain (`:94`); +0.20
  introduces a live packet-frame negative density 1.7e−4 (`:66-70`).
- (i) [L1]: by I3, any time-dependent R edit is a candidate Type IV source.

#### G15. Temporal edge profile and schedule of packet windows

- (a) Time-edge shape (tanh, minimum-jerk, smoothstep7) and schedule
  (live_only, entry_catch_release, catch_only, coordinated_release) of carve
  and lapse windows (`STAGE1_INFRA_DERIVATIVE_SMOOTHING_PROGRESS.md:19-32`).
- (b) 64 profile cases, 72 schedule cases.
- (c) Profiles: "did not improve the current candidate … the best rows were
  the existing `tanh` timing" (`:71`). Coordinated carve release: "live source
  fractions worsen sharply even though packet-norm safety still holds" (`:97`).
  Coordinated lapse (81×109): live T_kk 0.024255 → 0.016849, live p_l
  0.006986 → 0.008749, margin −5.456 → −3.860; the steepest lapse slope moves
  from 5.61 (non-live) to 10.21 (post-release, **live**) (`:119-141`).
- (d) SWEEP + single high-resolution check. (e) Measured.
- (f) Lapse retiming trims null burden by placing lapse-derivative burden in
  the live tube. "carve appears to preserve packet/support separation during
  transport and catch" (`:163`).
- (h) Derivative-limited time profiles bought nothing here; the hard `max`
  floor union has point-peak ratio 32.65 against 8.75 for `blend` (`:88-95`).

#### G16. Compact handoff: transition profile and width of the carve windows

- (a) Replace tanh carve-window transitions by finite-support smoothstep5/7
  profiles; "wide" multipliers (entry 4.8, catch 3.4, edge 7.2) spread the
  transition across the packet (`STAGE1_COMPACT_HANDOFF_COMPONENT_PROGRESS.md:14-27`).
- (b) Narrow compact5/compact7 vs tanh; wide3/wide4; edge carve 0.04–0.16;
  entry carve 0.70–0.80, entry width 4.2–5.4.
- (c) Narrow compact is much worse: live T_kk 9.745 (tanh) → 21.73 (compact5)
  → 30.46 (compact7); T_kk peak 0.958 → 7.24 → 12.73
  (`STAGE1_COMPACT_HANDOFF_COMPONENT_PROGRESS.md:53-55`): "Endpoint smoothness
  alone is not enough; the transition must be broad enough" (`:57`). Wide4 vs
  split_ref (61×83): live T_kk −10.8%, p_l +12.2%, j_l −10.2%, p_Ω −35.9%;
  T_kk peak +5.0%, p_Ω peak −32.5%; rel|∂²_lγ_ll| 1297.40 → 394.93 (−69.6%)
  (`STAGE1_COMPACT_HANDOFF_HIGHRES_FINDINGS.md:49-64, 93-105`). Top live p_Ω
  rows 18/20 → 10/20 (`STAGE1_SHELL_THROAT_OVERLAP_PROXY.md:108-115`).
- (d) SWEEP + high-resolution single comparisons. (e) Measured. The
  width-over-order result is consistent with G being linear in second
  derivatives (a transition of width Δ has second derivatives ∝ 1/Δ²),
  which no report derives.
- (f) "entry containment -> radial pressure balance / live p_l control; broad
  compact handoff -> angular-current relief / derivative concentration
  control; edge carve recovery -> live Tkk recovery with peak/current cost"
  (`STAGE1_COMPACT_HANDOFF_HIGHRES_FINDINGS.md:130-132`).
- (h) "Weakening entry actually worsens live `p_l`" (`:85`).
- (i) `compact7_wide4_edge160` became the promoted Stage II pair [L1 untested].

#### G17. Entry gate (`live_packet_start`)

- (a) An accounting boundary: points with σ < start are labelled pre-entry
  setup and leave live accounting. **No metric function changes**
  (`STAGE1_COMPACT_ENTRY_STAGE_SCREEN.md:16-28`; `source_ledger.py:2002-2004, 2037-2041`).
- (b) Unset, −1.40, −1.36, −1.32, −1.28.
- (c) Positive live packet-norm points 2 → 0; live T_kk 15.94 → 13.98
  (`STAGE1_COMPACT_ENTRY_STAGE_SCREEN.md:68-69`). The two positive-norm points
  at σ = −1.500 and −1.422 remain in the geometry
  (`STAGE2_HARD_AFFINE_SNEC_ADVERSARIAL.md:96-99`).
- (e) Definitional. (h) The −1.40/−1.36/−1.32 rows are identical at the grid
  spacing (`STAGE1_COMPACT_ENTRY_STAGE_SCREEN.md:83-85`).
- (i) "Live burden 0" statements downstream partly reflect this relabelling.
