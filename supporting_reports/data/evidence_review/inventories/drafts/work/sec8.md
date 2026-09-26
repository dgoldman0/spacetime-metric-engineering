## 8. Gaps

### 8.1 Channels never measured

- **Occupant physics.** No throat-era report computes passenger aging, tidal
  acceleration or occupant acceleration. The packet-norm sign is the only
  occupant readout, and [L2] applies to it.
- **Algebraic type.** Type was never tested for:
  - any Stage I knob (G7–G21);
  - R_th, V or w_Ω dynamically;
  - the shell partners.

  The Type IV attribution isolates decompression and moving windows only
  (G5).
- **Energy conditions beyond the radial NEC and the packet WEC.** SEC, DEC and
  the tangential NEC were never computed for geometry knobs. The static
  identity I19 (a clock maximum costs ρ+p_r+2p_t < 0) was never checked
  against any design.
- **Physical normalization.** Every burden is α²-weighted (I8) and
  coordinate-volume weighted. No lapse-normalized or proper-time-weighted
  burden was ever reported.
- **Arrival comparison.** The throat era has none; the first well-posed one is
  in the later one-space choreography pass [L3].

### 8.2 Knobs never varied

- **Plant constants.** C₀, λ, B₀, the shift exponent p_β, R_pass and the
  jacket amplitude a_Ω were never varied.
- **Shift amplitude.** It was never varied independently of V.
- **Join classes.** The receiver outer power was fixed at 0.5, and C1-only
  joins were never tested.
- **Radius sweep.** The R_th sweep is not a similarity transformation: w_th,
  w_Ω, R_pass and the time scales stay fixed. The 1/R² and R² scaling readings
  (G1) are therefore INVENTORY inferences, not controlled scaling results.
- **Throat-capacity partner.** No numbers are reported at nonzero ratios.
- **Clock-lapse partner.** Its isolated effect was never measured: there is
  no clock = 0 control at matched timing.
- **Shell half-width.** Widths narrower than the code minimum 0.48125 cannot
  be tested.
- **C1 handoff.** The handoff schedule was never computed. No
  quantum-inequality or ANEC bound was applied to the September sources.

### 8.3 Open questions the identities pose but the reports leave unanswered

- **Type IV necessity.** It is unknown whether every time-dependent stretch
  acting where R varies must produce Type IV. I2 and I3 give a necessary
  condition only. The 28 enthalpy zeros that make slowdown fail (I9) are not
  traced to specific profile features.
- **p_l invariance.** The live p_l fraction is invariant to V and to lapse
  (G8), and there is no derivation of why.
- **Receiver side asymmetry.** The mechanism behind the +l/−l asymmetry of
  the receiver (G25) is not derived.
- **Closure pattern.** The non-monotone V2/V2.5/V5/V10 closure pattern (G6)
  is unexplained.
- **SNEC floor normalization.** The harness floor is −1/(4τ²). A
  unit-normalized Freivogel–Krommydas form gives −B/τ², and the conversion is
  not derived (D2).
- **Unsampled catch interval.** The inventory's closed-form estimate predicts
  a V10 packet failure in the unsampled early-catch interval
  (σ ≈ −0.45 to −0.64). It remains unverified (G2).

### 8.4 Evidence hygiene issues the book should avoid inheriting

- **One-sided transfer metrics.** These disagree in sign with raw changes
  (§3.D).
- **Promotion on proxy metrics.** Promotions were made on proxies while the
  raw metric favoured the alternative (`mid` vs `outer`, G25).
- **Fits called passes.** Fits with normalized L1 > 1 were promoted on
  integrated ratios (M3; `STAGE2_BETA075_STRUCTURED_ENDPOINT_SOURCE_MODEL.md:97-100`,
  per the beta075 extraction).
- **Symmetry-guaranteed gates.** Examples are angular exchange = 0 and ADM
  re-projection at 10⁻¹⁷. These carry no evidential weight.
- **Relabelling counted as improvement.** The entry gate (G17) relabels
  points without changing the metric.
