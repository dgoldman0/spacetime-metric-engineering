### 3.F Source-model knobs on the beta075 demand (May 21 – 24)

Every entry here is **[β075]** (dense 377×241 and 189×121 meshes over
σ ∈ [−1.5, 15], l ∈ [−6, 6]; `STAGE2_BETA075_DENSE_ENDPOINT_SOURCE_STABILITY.md:19, 37, 41`).
Each is tagged **(Adm)** when its conclusion assumes a medium with a rest
frame can supply the demand — undermined by the Type IV layer [L1] — or
**(Geo)** when it reads only the demanded geometry. The cluster saw the Type
IV content in May: before regulation the endpoint-J sector was Type IV on
11.1% of volume and 25.9% of burden (`STAGE2_BETA075_ENDPOINT_SOURCE_CLASS_SCREEN.md:100-101`).
It then changed the stress (M1) rather than the geometry. The endpoint fit
later measured 46–48% off its J target (`LE_BOUNDARY_GATE_PREFLIGHT.md:115-119`),
and stored rest energies were wrong on most dense rows [L5]. No file in this
cluster reports passenger aging, tides or acceleration.

#### M1. Endpoint current regulator (safety factor) — (Adm)

- (a) Minimal Type I restoration: reg = max(0, 2|j_l| − |ρ+p_l|), added as
  δρ = δp_l = ½ sgn(ρ+p_l)·reg, scaled by a safety factor SF
  (`STAGE2_BETA075_ENDPOINT_CURRENT_REGULATOR_SCREEN.md:56-66`).
- (b) SF 1.00/1.05/1.10/1.25; depletion to ½, 1/10, 1%, 0.
- (c) Regulator/source 0.0377 → 0.0472 (baseline); p99 heat ratio 1.000
  (luminal) → 0.9465 (`STAGE2_BETA075_REGULATED_MEDIUM_ADMISSIBILITY_AUDIT.md:109-114`);
  0 post-regulator Type IV rows, 0 live regulator rows (regulator screen
  `:84-87`); local regulator/source ratio up to 1.0527 at the release support
  edge (`STAGE2_BETA075_BV_ANALOGUE_SOURCE_PATHOLOGY_MAP.md:116, 180-184`).
  Zero regulator: all 56 watch rows fail at unchanged cone margin
  (`STAGE2_BETA075_PRINCIPAL_SYMBOL_SENSITIVITY.md:21-24, 65-69`).
- (d) SWEEP. (e) The formula and its D = 0 endpoint at SF = 1 are GEN-I (I24).
- (h) The regulated tensor is not the Einstein demand.
- (i) Core (Adm) item: on the Type IV rows no rest-frame medium supplies the
  demand (`THROAT_GEOMETRY_CLARIFICATION.md:157-158`).

#### M2. Source class — (Adm)

- (b) Canonical scalar, phantom scalar, ordinary Type I anisotropic fluid,
  regulated anisotropic medium.
- (c) Scalar-compatible volume 0.380/0.336 (canonical) and 0.382/0.407
  (phantom); the Type I fluid fails because Type IV carries 0.2515/0.2590 of
  the burden; the regulated medium passes
  (`STAGE2_BETA075_ENDPOINT_SOURCE_CLASS_SCREEN.md:84-103`).
- (e) **GEN-I exclusion**: a minimally coupled scalar's radial block "is
  boost-diagonalizable and the signs of rho+p_l and p_l-pOmega are tied to the
  scalar kinetic sign" (`STAGE2_BETA075_MATTER_ACTION_FEASIBILITY_WORKLOG.md:79-81`),
  so it never supplies Type IV (I23).

#### M3. Support-reservoir ansatz and basis size — (Adm)

- (a) Exchange current J_support = P u + F s between endpoint medium and
  support, fitted by a smooth algebraic P/F form or by a phase-aware
  stroke/stress wave operator with basis, ridge and Laplacian options
  (`STAGE2_BETA075_SOURCE_FAMILY_EQUATION_PACKAGE.md:55-58`;
  `STAGE2_BETA075_SOURCE_FAMILY_VALIDATION.md:44-52`).
- (c) Smooth P/F: best normalized L1 0.614/0.793 (fails 0.50). Stroke/stress
  24×14: 0.223/0.449 (passes) with 13,088/15,527 effective coefficients against
  28,359 active rows; Laplacian off on dense 0.5688 (fails); total closure
  local P/F 0.5446 against a 0.55 gate
  (`STAGE2_BETA075_MATTER_ACTION_FEASIBILITY_WORKLOG.md:896-915, 1116-1139, 1367-1373, 1524-1531`).
- (e) DESIGN. The split ∇·T_endpoint + J = 0 is GEN-I, and J_perp = 0 is forced
  by spherical symmetry, so "angular exchange absence" gates carry no evidential
  weight (INVENTORY DERIVATION). The support tensor's type is left free by its
  divergence (I15).
- (h) A near-interpolating basis passes; ~45% (L2) of the endpoint divergence
  remains uncancelled at "pass".

#### M4. Source-time class and service-aligned scheduling — (Adm, transport)

- (b) Observed schedule; service-aligned pulses of 1–47 steps; convex-kernel
  envelope; common jitter radius 0–8 (165 cases); arbitrary impulse.
- (c) Max budget fraction 0.121 (observed) → 0.176–0.194 (widest aligned pulse)
  → 0.743 (1-step pulse and convex envelope; unchanged under jitter) → 1.159
  (arbitrary impulse, fail) (`STAGE2_BETA075_FULL_SYSTEM_FIXED_BACKGROUND_EVOLUTION.md:23-28`;
  `STAGE2_BETA075_SERVICE_ALIGNED_SCHEDULE.md:47-66`;
  `STAGE2_BETA075_TIMING_JITTER_CERTIFICATE.md:38-55`;
  `STAGE2_BETA075_ACTION_PDE_PROOF_OBLIGATION.md:48-51`).
- (e) The convex-kernel bound is a DERIVATION: "The one-step service-aligned
  basis response bounds any common nonnegative temporal kernel over the same
  service-ordered source bins by linearity and positivity of the transport
  operator" (`STAGE2_BETA075_ALIGNED_ENVELOPE_CERTIFICATE.md:14-16`). It holds
  for any linear positive transport; magnitudes DESIGN.
- (h) With the same source, schedule order alone moves the budget 0.12 → 0.74 → 1.16.

#### M5. Heat-current rapidity: evolution variable, kick amplitude, injection form — (Adm, transport)

- (c) Raw heat ratio +1e−4 fails, rapidity +1e−4 passes (margin 2.25e−5,
  independent of damping) (`STAGE2_BETA075_REDUCED_TRANSPORT_EVOLUTION_PILOT.md:13-20`);
  large (5×) impulse budget 1.434 fails, distributed pulse 0.850 passes
  (`STAGE2_BETA075_RAPIDITY_BUDGET_DIAGNOSTIC.md:28`;
  `STAGE2_BETA075_SUPPORT_SOURCE_DYNAMICS.md:25-29`).
- (e) **GEN-I link** (I25): the heat-mode margin equals the Type I margin; the
  minimum cone margin 7.881e−5 and transport margin 7.983e−5 sit on the same
  row (`STAGE2_BETA075_REDUCED_PRINCIPAL_SYMBOL_HYPERBOLICITY.md:43`;
  `STAGE2_BETA075_RAPIDITY_BUDGET_DIAGNOSTIC.md:28`). These "transport"
  results are therefore not geometric-only: on Type IV rows v_q > 1 and the
  rapidity is undefined.
- (h) Spreading the same large source in time turns a fail into a pass.

#### M6. Support-edge source reshaping (cap 0.95) — (Adm, transport)

- (c) Smoothing leaves overdrive at 2.0 (2.0756 → 1.9997); a per-slice cap at
  0.95 of local budget brings outward/inward to 0.289/0.373, with slice scales
  down to 0.093, and moves the large-amplitude failure to release (1.445)
  (`STAGE2_BETA075_SUPPORT_EDGE_SOURCE_RESHAPING.md:61-114`).
- (h) Smoothing does not repair amplitude overdrive; normalization does, at
  the cost of sharp scale jumps.

#### M7. Mesh resolution (189×121 → 377×241) — mixed

- (c) Integrated channel totals agree within ~1%
  (`STAGE2_BETA075_DENSE_ENDPOINT_SOURCE_STABILITY.md:93-98`); extrema degrade:
  max live packet norm −9.935 → −6.334 (`:84-85`), min cone margin 2.41e−4 →
  7.88e−5 (`STAGE2_BETA075_REDUCED_PRINCIPAL_SYMBOL_HYPERBOLICITY.md:34-35`),
  reset-cap edge-tail fit coefficient 1.067 → 4.828 (`STAGE2_BETA075_DENSE_ENDPOINT_SOURCE_STABILITY.md:158-159`).
- (h) Integrated demand converges while minima keep shrinking — consistent
  with the singular receiver edge and thin Type IV layer later found (G25, G28).
  Packet norm (Geo) [L2]; the rest (Adm).

#### M8. 3+1 "backreaction" scenario amplitude — (Adm)

- (c) No Einstein solve: the driver is the residual ∇·(T_endpoint + T_support),
  propagated with scenario multipliers ≤1.0588; mean driver 0.476/0.55, peak
  1.652/1.75 (`STAGE2_BETA075_FIRST_ORDER_3P1_COUPLING.md:61-66`;
  `STAGE2_BETA075_MODERATE_3P1_V5_CAPSTONE.md:48-75`); the light version was
  demoted to a "light local off-axis/backreaction proxy"
  (`STAGE2_BETA075_3P1_BACKREACTION_CAPSTONE.md:7-14`).
- (i) (Adm): the driver comes from fitted sources.

### 3.G Demand-decomposition and diagnostic choices (May 19 – 24)

These change how the demand is read, not the metric. They matter for the book
because they decided verdicts.

#### D1. Source-role partition (A–I oracle roles; composite ansatz)

- (a) Assignment of demand by channel, stage, region and live flag to roles
  A (infrastructure radial null) … I
  (`STAGE2_COMPONENT_SOURCE_LEDGER_PROMOTED_PAIR.md:20, 26-47`).
- (c) Coverage 0.99 (radial null), 0.72 (pressure), 0.34–0.40 (current);
  live residuals 0 "should not be read as physical closure" (`:57-58, 77-80`).
  Fitted sector ratios: infrastructure p_l/ρ = −1.002; live trim p_l/ρ = −1.148;
  current relaxation H ρ/j = 0.115 (`STAGE2_COMPOSITE_SOURCE_ANSATZ_PROMOTED_PAIR.md:60-65, 92-93`).
- (e) Accounting. INVENTORY DERIVATION from the fitted means: H is
  flux-dominated (|ρ+p_l| = 0.011|j| < 2|j|), i.e. Type IV; the near-saturated
  string-cloud fit p_l/ρ = −0.999288, j/ρ = −0.000485
  (`STAGE2_ENTRY_SECTOR_CLOSURE_DENSE.md:124-125`) gives radial null energies
  of opposite sign — a tiny current flips a string cloud to Type IV.
- (h) The "constant-flux string cloud" Φ = 0.039772 is the geometry's own
  W-term ≈ 1/(8π) (I12), not an independent matter finding.
- (i) Promoted pair and entry-gated geometry (pre-beta075); type untested.

#### D2. SNEC smearing width, coverage filter, domain and parameterization

- (a) Gaussian smearing width τ of the null-projected stress along radial
  rays; a scoreability filter (≥80% support and kernel coverage); lapse vs
  affine parameter; harness floor −8πB/τ² with B = 1/(32π)
  (`STAGE2_HARD_AFFINE_SNEC_PROMOTED_PAIR.md:22-43`;
  `STAGE2_HARD_AFFINE_SNEC_ADVERSARIAL.md:25-29`;
  `STAGE2_AFFINE_REPARAM_SNEC_AUDIT.md:17-24`).
- (c) Margin shrinks with τ (15.97 at τ = 0.125 → 0.0412 at τ = 2) because the
  floor scales as τ⁻² while smeared stress saturates
  (`STAGE2_HARD_AFFINE_SNEC_ROBUSTNESS.md:42-53`). Scoreability flips verdicts:
  189 raw violations and 0 scoreable at τ = 4 on 81×109
  (`STAGE2_HARD_AFFINE_SNEC_ADVERSARIAL.md:73`). Affine non-affinity is large
  (max dλ/dσ 1291) yet the beta075 run stays clean: 0 violations in 175,851
  windows (`STAGE2_AFFINE_REPARAM_SNEC_AUDIT.md:106-107, 130-133, 171-172`).
  The finite-domain ANEC total on beta075 is negative (worst −1.797/−1.143),
  dominated by the closure residual
  (`STAGE2_BETA075_FINITE_DOMAIN_RADIAL_ANEC_DIAGNOSTIC.md:60-73`).
- (e) Screen on demanded channels, "not a physical SNEC". INVENTORY flag: the
  integrand stays the orthonormal T̂_kk (only the measure is affine), and the
  harness floor −1/(4τ²) is 8π looser than the unit-normalized
  Freivogel–Krommydas form −B/τ²; the extended-domain scoreable values
  −0.00261 (τ = 2) and −0.00069 (τ = 4) would fail the tighter form
  (identities extraction; unverified against the literature normalization).
- (h) SNEC-clean does not imply finite-domain ANEC-clean.
- (i) Only the beta075 package was rerun with affine λ [β075]; promoted-pair
  results remain lapse-parameterized.

#### D3. Nonminimal scalar source screen (profile × φ₀ × ξ)

- (b) 5 profiles, φ₀ ∈ {0.05 … 1}, ξ ∈ {0, 1/6, 0.5, 1}; a localized fixed-metric
  solve (`STAGE2_PROMOTED_PAIR_SCALAR_KILL_SCREEN_PROGRESS.md:49-70`).
- (c) Best radial-null coverage 0.0072 at ξ = 1; top-20 demand/supply overlap
  0/20 (the scalar's negative T_kk lands in reset rows, the demand in
  entry/catch rows); localized solve 7.77×10⁻⁶ (`:87-88, 142-171, 228-232`).
- (e) Measured; minimally coupled canonical fields supply none by I23.
