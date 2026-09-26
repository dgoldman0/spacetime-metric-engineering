### 3.E Regularity repairs, reset sources and the constant-radius rule (Sept 8 – 23)

These are the LE repair attempts on the frozen beta075 geometry, plus the
design rule that closed the era. All use the repaired classifier. Every entry
is **[β075]** except G31, which replaces the geometry.

#### G28. Join regularity: receiver cusp, origin kink, shell cap

- (a) Smoothness class of the joins where localized metric edits switch on:
  the receiver's u^{1/2} inner edge (√ cusp) and clipped outer edge (slope
  jump), replaced by quintic Hermite C2 ends; the |l| kink of the lapse
  shoulder and shell radius at l = 0, replaced by
  r_a = a(15/8 t² − 5/4 t⁴ + 3/8 t⁶) inside a = 0.1; the shell's temporal cap,
  which began at a nonzero Gaussian slope, replaced by a C2 quintic cap
  (`LE_RECEIVER_C2_REPAIR_ATTEMPT.md:28-35`; `LE_BOUNDED_METRIC_REPAIR.md:26-46`).
- (b) √ cusp vs C2; blend fraction 0.0625/0.125/0.25; control receiver gain 0;
  origin a = 0.1 vs kink; control η_N = 0; cap slope jump vs C2.
- (c) *Receiver inner edge*: frozen density −0.064 → −107.6 over five step
  halvings, ×2^{3/2} per halving (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:171-180`);
  repaired 0.013457 → 0.013684, approaching the receiver-free value 0.013686
  (`LE_RECEIVER_C2_REPAIR_ATTEMPT.md:66-77`). One-sided absolute stress
  integral over [ε, 0.02]: frozen 0.001205/0.003796/0.012015 for ε =
  10⁻³/10⁻⁴/10⁻⁵ (unbounded, ∝ ε^{−1/2}); repaired static 0.000408/0.000430/
  0.000432 (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:190-199`; `LE_RECEIVER_C2_REPAIR_ATTEMPT.md:89-93`).
  *Outer clip*: density ∝ h⁻¹ (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:185-188`).
  *Origin*: angular pressure 0.001905 → 0.025804 (∝ h⁻¹) with the kink,
  ≈0.0017263 across eight levels after repair (`LE_BOUNDED_METRIC_REPAIR.md:57-61`).
  *Shell cap*: the slope jump (−4.70514 in the shift derivative) gave finite
  sampled G at the join (`LE_BOUNDED_METRIC_REPAIR.md:49-55`).
  *Algebraic type*: unchanged — the 104 Type IV witnesses outside the repair
  bands have bit-identical tensors; 1,365 vs 1,361 active Type IV samples;
  the repaired inner edge is "finite and Type IV" (`LE_RECEIVER_C2_REPAIR_ATTEMPT.md:100-120`).
  *Packet/service*: not re-evaluated.
- (d) DERIVATION ("The metric is continuous with a square-root cusp there.
  Its second radial derivative grows as d^{−3/2}", `LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:167-169`)
  + SWEEP (refinement ladders) + CONTROL.
- (e) **GEN-I** (I13): stress growth follows the join class — √ cusp
  divergent and non-integrable, slope jump h⁻¹ surface term, C2 first-order
  convergent, C∞ scheme-order convergent. Coefficients DESIGN.
- (f) Blend fraction changes burdens by < 0.3%.
- (g) **Decoupling**: repairs are exactly local — "These witnesses lie outside
  the repair bands, including their curvature stencils, so this equality is a
  direct locality check" (`LE_RECEIVER_C2_REPAIR_ATTEMPT.md:102-104`). Regularity
  and algebraic type decouple.
- (h) Removing the singular term reveals Type IV beneath it: "the original
  singular term had dominated its classification" (`:119-120`). After repair
  the active edge burden is ~10× the static one (0.004625 vs 0.000432). A
  temporal slope jump gave no measured divergence, unexplained.
- (i) Local success; gate still fails (`LE_BOUNDED_METRIC_REPAIR.md:236-249`).
  Superseded by C∞ primitives on the constant-R track
  (`CONSTANT_RADIUS_TRACK.md:122-137`). C1-only joins never tested.

#### G29. Coupled reset source: tangential material plus two null streams

- (a) Replace the demanded reset stress by an explicit source: released string
  pairs B, a positive-enthalpy material of density F with p_t/ρ = 1/4, and two
  counter-streaming null streams, blended by a C2 handoff window
  (`LE_COUPLED_RESET_SOURCE_ATTEMPT.md:62-93`).
- (b) One registered value per parameter, 9 phases × 3 resolutions.
- (c) 2,030 Type IV of 8,253 samples (`:151-153`). At the old witness Δ turns
  from −0.00206 to +0.00123 (Type I), and a new converged Type IV witness
  appears at l = −2.133 inside the source plateau, plus Type IV at σ = 2.6
  where the reference had none (`:168-191`). Mass: the areal-gauge constraint
  needs δm ≈ 1.433 where ≈0.533 is available before f = 0; f reaches −0.61 at
  reset (`:196-210`).
- (d) SINGLE; mechanism is DERIVATION: "h_total=E+P_r=h_b+3F, Δ=(h_b+3F)²−4J²
  … the energy change 2F−B enters the Hamiltonian equation and consumes more
  radial mass allowance than this geometry provides" (`:229-243`).
- (e) Mass relation GEN-I (I27); the enthalpy relation is an identity of this
  prescription.
- (f) Positive-enthalpy material helps Type IV and costs mass: "These two
  requirements therefore need a common source and geometry construction"
  (`:246-247`).
- (g) "Changing the tangential-pressure ratio alone leaves both failing
  expressions unchanged" (`:243-244`); B cancels from the enthalpy.
- (h) Fixing one witness moves Type IV outward into the source plateau.
- (i) Stopped; superseded by G30 and G31.

#### G30. Reset inverse search: geometry path and moving infrastructure

- (a) Ten controls on the reset geometry and source (duration, offsets,
  donor/reservoir placement), a direct blend vs a path through rest
  waypoints, and stationary vs moving (|v| ≤ 0.5) infrastructure
  (`LE_RESET_INVERSE_SEARCH.md:64-125, 168-187`).
- (b) 1,024 Sobol points, 16 boundary seeds, 8 Powell solves.
- (c) Best objective: direct/stationary 0.3015, direct/moving 0.2523,
  waypoints 38.5/37.6 (`:263-270`). Best moving candidate: minimum material
  density −5.92×10⁻⁵ vs −2.56×10⁻³ stationary (≈43×), radial margin
  −7.30×10⁻⁴ (Type IV remains), angular mismatch 2.86×10⁻³ vs 1.49×10⁻³
  (`:282-286`). Type IV persists at positive density (`:305-310`). 780
  controls exhausted the lapse range and remain undecided (`:272-274`).
- (d) SWEEP + DERIVATION of an onset obstruction (I28).
- (e) The obstruction holds "for these source families and boundary
  conditions" (`:419-421`); boosting infrastructure preserves the radial
  discriminant (I26), so motion alone cannot cure Type IV.
- (f) Moving infrastructure trades material deficit against angular mismatch,
  speed saturation and a lapse shift of up to 93% (`:312-316`).
- (h) The direct path beats rest waypoints by >100× in objective.
- (i) Stopped; superseded by G31.

#### G31. Constant areal radius wherever the metric evolves (post-era design rule, Sept 23)

- (a) "Hold the areal radius constant wherever the service metric evolves, and
  confine every variation of the radius to regions where the geometry is
  static" (`CONSTANT_RADIUS_TRACK.md:73-76`). Knobs within it: track radius
  R_b, half-length L_b, end-transition width Δ, decompression schedule.
- (b) R_b 1.4/1.75/2.14; L_b 4.5/5/6; Δ 0.75/1.5/3; five decompression
  schedules (`CONSTANT_RADIUS_TRACK.md:181-185, 297-303`).
- (c) Type IV 13,587 → 0 of 141,661; min T₊T₋ −2.079×10⁻³ → 0; max |j|
  0.0230 → 0 (`:171-176`); all 40,071 points Type I across R_b/L_b variants
  (`:181-183`). Live corridor: min T_kk −0.656 → 0; min packet-frame density
  −1.33×10⁻³ → +0.012992 = 1/(8πR_b²) (`:269-274`). Packet norms, null speeds,
  carrying flow and schedule unchanged, −9.935129 (`:115-116, 233`).
  Both-shrinking traces 77 → 0 (`:233-243`). Cost: angular NEC fails where
  K > 1/R_b² (min ρ+p_Ω −0.0741) (`:269-274, 288-292`). End transitions:
  peak static radial deficit −0.118/−0.058/−0.028 for Δ = 0.75/1.5/3 at fixed
  integrated opening 2.000001 (`:183-185, 325-326`).
- (d) IDENTITY (I4, I18) + SWEEP.
- (e) **GEN-I**: the Type IV removal, the string-cloud radial block, the
  transfer of all 2D dynamics to p_Ω = −K/8π, the invariance of packet
  kinematics under B edits, and peak ∝ 1/Δ at fixed opening all follow from
  I1–I4 and I18.
- (g) **Decoupling identity**: "Packet norms, radial null speeds, the carrying
  flow and the service schedule depend only on (α,β,γ_ℓℓ)" (`:115-116`).
- (h) The throat-era "S0 string cloud" becomes exact: "ρR_b²=1/(8π) … the S_0
  role, now exact" (`:346-348`).
- (i) Post-era. Still two-ended [L4]; the end transitions "follow from the
  reduced model's two asymptotic ends" (`:119-120`). Service ratios still use
  l = σ [L3]. The one-space axial track later moves the Type IV question into
  its transverse boundary layer (`:338-342`).
