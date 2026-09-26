### 3.C Support-shell overlay (V5/V10, May 16 – 17)

The shell is an infrastructure-local shift actuator δβ_shell = A·W_shell in the
annulus 0.65–1.20 R_th, excluding the packet, with optional exp(gain·W_shell)
partners on α (clock-lapse), A (rail-stretch) and B (throat-capacity)
(`V5_CONTINUOUS_SUPPORT_SHELL_4D_SOURCE_SWEEP.md:12, 18, 35-37`;
`source_ledger.py:492-551, 1487-1499, 1556`). Two ledgers are used: the reduced
ADM constraint ledger (PDF eqs. (13)–(17), with β-off substrate subtraction)
and the 4D point ledger.

#### G18. Shell amplitude and sign

- (a) Peak added shift in the support-edge annulus.
- (b) 1e−7 … 2.0, both signs, 27×37; 0.5 and 1.0 at 53×73
  (`V5_CONTINUOUS_SUPPORT_SHELL_4D_SOURCE_SWEEP.md:120-163`); signed-objective
  pairs at V5 (14) and V10 (16).
- (c) *Packet*: 0 failures through amplitude 2.0; packet drift exactly
  linear, 1.71028e−4 at 1e−3 → 0.171028 at 1.0. *Demand*: onset of visible
  burden growth at 1e−3 to 1e−2; at 0.5: max total ratio 1.0909, radial null
  1.0562, radial current 1.040, p_l 1.000013, point peak 1.286; at 1.0: null
  1.1339, current 1.0804, point peak 2.539. Live-packet burden changes 10⁻⁵ to
  10⁻¹⁰: all added demand lands outside the packet
  (`V5_CONTINUOUS_SUPPORT_SHELL_4D_SOURCE_SWEEP.md:120-184`). *Sign*: positive
  wins all pairs by ≤2.89e−6 (V5) and ≤1.53e−5 (V10)
  (`V5_SIGNED_SOURCE_OBJECTIVE_SIGN_TEST.md:36`; `V10_SIGNED_SOURCE_OBJECTIVE_SIGN_TEST.md:34`):
  "treat this as a numerical tie-breaker, not a physical source conclusion"
  (`V5_SIGNED_SOURCE_OBJECTIVE_SIGN_TEST.md:60`). At amplitude 1.0 the sign
  matters in the packet-frame density: neg-ρ_packet ratio 1.4157 (negative)
  vs 1.000008 (positive) (`V5_CONTINUOUS_SUPPORT_SHELL_4D_SOURCE_SWEEP.md:162-163`).
- (d) SWEEP.
- (e) DESIGN magnitudes. **GEN-I structure** (INVENTORY DERIVATION from PDF
  eqs. (9)–(14)): j_l is affine in β at fixed (α, A, B), so small actuators
  route demand sign-symmetrically; sign enters only through alignment with the
  baseline current, |b + εδ| − |b| ≈ ε·sgn(b)·δ, which is why the gaps are tiny.
  Sign becomes physical only in channels nonlinear in β (ρ_packet).
- (f) "The overlay changes the off-diagonal carrying-flow part of the metric
  while leaving the clock-lapse, rail-stretch, and throat-capacity parts
  unchanged" (`V5_CONTINUOUS_SUPPORT_SHELL_4D_SOURCE_SWEEP.md:226`); load
  bearing "likely requires coupled metric shaping" (`:299`).
- (g) Moves radial-null and current channels; p_l and packet safety fixed.
- (h) Packet-safe over a 10⁷-fold amplitude range, yet it only adds demand.
  At V10 the reduced-ADM routing is "only about `3.21e-6` of the V10 baseline
  global `delta_j_l` burden" (`V10_SUPPORT_SHELL_EDGE_STRESS.md:77`).
- (i) [L1] 60 dense Type IV points on the shell transition
  (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:87`); [L2]. No report checks g_σσ in the
  shell; the pre-stage extraction estimates α/√A ≈ 0.6 at the annulus centre,
  so amplitudes near 1 may tip the radial cones there (unverified).

#### G19. Shell timing: catch lead, temporal width, profile

- (a) Pulse centred at x_catch_packet − lead, normalized at the catch-window
  start, width w.
- (b) Reduced ADM: leads 0–1.25, widths 0.25–1.0; 4D: leads 1.0–1.55, widths
  0.25–0.40, gaussian/raised-cosine/minjerk.
- (c) 4D lead scan at width 0.30 (`V5_HIGHRES_COUPLED_TIMING_SOURCE_FEASIBILITY.md:53, 65-66`):

| lead | radial null | radial current | packet drift |
|---:|---:|---:|---:|
| 1.35 | 1.027862 | 1.014999 | 0.024236 |
| 1.45 | 1.024110 | 1.013124 | 0.021838 |
| 1.55 | 1.021197 | 1.011647 | 0.019676 |

  Width 0.30 cleaner than 0.35/0.40 (`:45`); the best width shifts to 0.35 as
  strength rises (`V5_SUPPORT_SHELL_SHAPE_ROBUSTNESS_REPORT.md:184`). Width
  0.25: neg-ρ_packet ratio 1.3068 while packet drift is 3.16e−8 (`:171-182`).
- (d) SWEEP. (e) DESIGN.
- (h) "The active metric can keep the live packet norm safe while still
  producing a packet-comoving source-accounting penalty elsewhere in the grid"
  (`V5_SUPPORT_SHELL_SHAPE_ROBUSTNESS_REPORT.md:182`).
- (i) [L1] [L2].

#### G20. Shell metric partners: clock-lapse, rail-stretch, throat-capacity (κ_Q/a_β)

- (a) Each partner multiplies one metric function by exp(gain·W_shell), gain
  = a_β × ratio. Verbatim for the throat-capacity partner:
  "G_throat(s,l) = G_throat_base(s,l) * exp(kappa_Q * W_shell(s,l)),
  kappa_Q = a_beta * throat_capacity_ratio"
  (`V5_HIGHRES_COUPLED_TIMING_SOURCE_FEASIBILITY.md:173-174`).
- (b) a_β = 0.5; clock ratios 0.25/0.375/0.5; rail ratios 0/0.25/0.5; throat
  ratios −0.5 … +0.5 (`V5_THROAT_CAPACITY_AND_GRADIENT_MATCHING_NOTE.md:6-12`;
  `STAGE1_V5_THROAT_CAPACITY_SOURCE_PLACEMENT.md:41-51`).
- (c) *Clock-lapse*: best cases max burden 1.053–1.054, radial null
  1.020–1.028, current 1.012–1.015, angular pressure sets the max channel
  (`V5_HIGHRES_COUPLED_TIMING_SOURCE_FEASIBILITY.md:89`); ~88% of the added
  radial-current burden lands in the shell–throat overlap band (`:91`).
  *Rail-stretch*: best max burden 1.0534 (0) → 1.0594 (0.25) → 1.0682 (0.5)
  (`:78-80`). *Throat-capacity*: best objective at ratio 0 (1.0974); −0.05
  lowers radial null 1.01995 → 1.01209 but raises current 1.0118 → 1.0205 and
  point peak 1.183 → 1.762; +0.05 puts max total and null in 1.079–1.080 with
  point peaks >2.68× (`STAGE1_V5_THROAT_CAPACITY_SOURCE_PLACEMENT.md:57-80`);
  "the throat-capacity partner trades angular/throat shaping against
  radial-null/current and point-peak penalties too aggressively" (`:68`);
  "the failure mode is not packet causality" (`:68`).
- (d) SWEEP.
- (e) DESIGN. The report's summary "timing and gradient matching dominate
  amplitude tuning" (`V5_THROAT_CAPACITY_AND_GRADIENT_MATCHING_NOTE.md:31`) is a
  reading of these sweeps, not a derivation.
- (f) Clock 0.5 favours aggregate burden, 0.375 favours packet drift and
  shell–throat concentration (`V5_HIGHRES_COUPLED_TIMING_SOURCE_FEASIBILITY.md:105, 279`).
- (h) **Confound**: the "coupled clock helps" comparison against the
  carrying-flow-only shell (max 1.0909) also changed lead and width
  (1.0/0.35 → 1.35–1.55/0.30), and the 81-case grid has no clock = 0 control
  (pre-stage extraction). The isolated clock effect is untested.
- (i) Throat-capacity edits R where the metric evolves, which I3 identifies as
  the Type IV mechanism and G31 forbids; its measured sharp null penalty
  points the same way [L1]. Stage I-A closed with throat capacity = 0
  (`STAGE1_V5_THROAT_CAPACITY_SOURCE_PLACEMENT.md:110`).

#### G21. Shell radial profile, radial half-width and strength band

- (a) Radial window shape (raised-cosine annulus, Gaussian annulus, smooth
  box), half-width, and matched strength: "abs_amplitude * max |W_shell| =
  target_delta_beta_abs_max." (`V5_SUPPORT_SHELL_SHAPE_ROBUSTNESS_REPORT.md:27`).
- (b) 48 matched-shape cases, 40 width cases, 120 strength cases
  (`GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md:35`); strengths 0.15–0.35.
- (c) Shape at matched strength 0.25 (`V5_SUPPORT_SHELL_SHAPE_ROBUSTNESS_REPORT.md:113-115`):

| profile | max burden | packet drift | radial null | radial current |
|---|---:|---:|---:|---:|
| raised-cosine annulus | 1.013261 | 3.09e−8 | 1.007942 | 1.002684 |
| Gaussian annulus | 1.016165 | 1.51e−3 | 1.008492 | 1.003251 |
| smooth box | 1.052003 | 1.81e−2 | 1.019290 | 1.011380 |

  Half-width 0.48125 → 1.00: max burden 1.0133 → 1.0379, packet drift 3.09e−8
  → 3.13 (`:131-137`); 0.48125 is the code minimum, so narrower widths were
  untestable (pre-stage extraction). Strength ladder 0.15 → 0.35: max burden
  1.0083 → 1.0180 (≈0.05 per unit peak δβ, near-linear), point peak 1.000 →
  1.294 (superlinear above 0.25); drift < 1e−6 throughout (`:147-161`).
- (d) SWEEP. (e) DESIGN. INVENTORY INFERENCE: the raised-cosine annulus is
  compactly supported on the support-edge band while Gaussian and tanh-edged
  profiles have tails reaching the packet, consistent with the 10⁵-fold drift
  spread.
- (g) Aggregate burden linear in strength; point peak decouples above 0.25.
- (h) Compact support, not smoothness order alone, keeps the occupant readout
  quiet.
- (i) The September construction manifest uses a smooth-box shell, "so the old
  shape winner has a separate lineage" (`GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md:35`);
  regularity repair covers only the smooth-box/Gaussian shell (`:124-126`) [L1] [L2].
