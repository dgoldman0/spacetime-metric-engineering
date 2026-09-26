## 4. Source-model knobs on the prescribed demand (May 19 – 24)

These knobs choose how a matter model is fitted to a fixed Einstein demand;
the metric does not change. All rest on one geometry (beta075 p003_mid with
the w6_t1p5 collar, or the pre-beta075 promoted pair) and are
admissibility-dependent: [L1] undermines every conclusion that the fitted
medium supplies the demand, because on the Type IV rows no rest-frame medium
can (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:112-114`). The pre-flight adds that
the frozen endpoint fit misses the original J target by 46.4–48.1%
(`LE_BOUNDARY_GATE_PREFLIGHT.md:115-119`), that the S0/J/core intermediate
model covers ~34% of the grid (`:97-102`), and that stored rest energies
disagree with the correct branch on 26,929 dense rows [L5]. "Pass" below means
a project-set threshold, not a physical bound.

#### M1. Endpoint current regulator (safety factor)

- (a) reg = max(0, 2|j_l| − |ρ+p_l|), added as δρ = δp_l = ½sgn(ρ+p_l)·reg
  × SF (`STAGE2_BETA075_ENDPOINT_CURRENT_REGULATOR_SCREEN.md:56-66`).
- (b) SF 1.00/1.05/1.10/1.25; depletion to 0.
- (c) Before regulation the endpoint sector was Type IV on 11.1% of volume
  and 25.9% of burden (`STAGE2_BETA075_ENDPOINT_SOURCE_CLASS_SCREEN.md:100-101`);
  after, 0 Type IV rows and 0 live regulator rows; regulator/source 0.039 →
  0.049 over SF 1.00 → 1.25; p99 heat ratio 1.000 → 0.9465
  (`STAGE2_BETA075_REGULATED_MEDIUM_ADMISSIBILITY_AUDIT.md:109-114`); local
  maximum regulator/source 1.0527 at release-fade support edge
  (`STAGE2_BETA075_BV_ANALOGUE_SOURCE_PATHOLOGY_MAP.md:116`). At zero regulator
  all 56 watch rows fail (`STAGE2_BETA075_PRINCIPAL_SYMBOL_SENSITIVITY.md:21-24`).
- (e) **GEN-I** (I24): the minimal regulator makes D = 0 exactly; it is a
  change to T, not a property of the demand.
- (i) Invalidated as a source conclusion by [L1].

#### M2. Source class (canonical scalar, phantom scalar, Type I fluid, regulated medium)

- (c) Canonical-scalar compatible volume 0.380/0.336 (baseline/dense);
  phantom 0.382/0.407; ordinary Type I fluid fails because Type IV carries
  0.2515/0.2590 of the burden (`STAGE2_BETA075_ENDPOINT_SOURCE_CLASS_SCREEN.md:84-103`).
- (e) **GEN-I**: a minimally coupled scalar is never Type IV (I23) and a
  canonical field supplies no null deficit, so these exclusions are algebraic.
- (i) [L1] [L5].

#### M3. Endpoint source-family basis (generic RBF vs structured modes vs no-tail body)

- (c) Support-edge selected/current/p_Ω ratios: generic 8×6 1.292/1.364/1.875;
  generic 12×8 1.207/1.188/1.402 with max coefficient 9.47; structured
  1.184/1.149/1.153 with max coefficient 0.445
  (`STAGE2_BETA075_ENDPOINT_J_SOURCE_FAMILY_RUNG.md:122-133`;
  `STAGE2_BETA075_STRUCTURED_ENDPOINT_SOURCE_MODEL.md:86-87`); component
  normalized L1 errors still > 1 for ρ, p_l, p_Ω (`:97-100`). Reset cap: tailed
  fit coefficient 1.067 → 4.828 under refinement, no-tail body bounded
  0.0919 → 0.0933 (`STAGE2_BETA075_DENSE_ENDPOINT_SOURCE_STABILITY.md:158`;
  `STAGE2_BETA075_ENDPOINT_SOURCE_FREEZE_REPORT.md:75-79`).
- (e) DESIGN. (f) Pointwise accuracy against coefficient boundedness.
- (i) [L1]: the fit target includes Type IV rows.

#### M4. Support-reservoir exchange model (ansatz, basis, Laplacian)

- (a) The endpoint divergence is absorbed by J_support = P u + F s (general
  split, `STAGE2_BETA075_SOURCE_FAMILY_EQUATION_PACKAGE.md:55-58`); J_perp = 0
  by spherical symmetry (INVENTORY DERIVATION). The reservoir operator is a
  model choice.
- (c) Smooth algebraic P/F: best normalized L1 0.614/0.793 (fails 0.50);
  stroke/stress 24×14: 0.223/0.449 (passes) with 13,088/15,527 effective
  coefficients against 28,359 active rows; Laplacian off on dense: 0.5688
  (fails); total closure active residual/endpoint L2 0.451, local P/F 0.5446
  against a 0.55 gate (`STAGE2_BETA075_MATTER_ACTION_FEASIBILITY_WORKLOG.md:896-915, 1116-1139, 1367-1373, 1524-1531`).
- (e) DESIGN. The divergence-form preference is structural: the exchange is
  itself a divergence of T.
- (h) Near-interpolation coefficient counts; ~45% (L2) of the divergence left
  uncancelled still counts as a pass and is reused as the "Bianchi driver"
  (`STAGE2_BETA075_FIRST_ORDER_3P1_COUPLING.md:101`).
- (i) [L1]; support tensor type undetermined (I15).

#### M5. Source timing class (observed schedule, service-aligned pulses, impulses, jitter)

- (c) Max transport-budget fraction for the same source: observed schedule
  0.121; widest aligned pulse 0.176–0.194; 1-step aligned pulse 0.743;
  convex-kernel envelope 0.743; common jitter radius 0–8 unchanged 0.743;
  arbitrary impulse 1.159 (fails) (`STAGE2_BETA075_FULL_SYSTEM_FIXED_BACKGROUND_EVOLUTION.md:23-28`;
  `STAGE2_BETA075_SERVICE_ALIGNED_SCHEDULE.md:47-66`;
  `STAGE2_BETA075_ALIGNED_ENVELOPE_CERTIFICATE.md:44-56`;
  `STAGE2_BETA075_TIMING_JITTER_CERTIFICATE.md:38-55`;
  `STAGE2_BETA075_ACTION_PDE_PROOF_OBLIGATION.md:48-51`).
- (e) Convex-kernel bound GEN (numerical analysis): "The one-step
  service-aligned basis response bounds any common nonnegative temporal kernel
  over the same service-ordered source bins by linearity and positivity of the
  transport operator" (`STAGE2_BETA075_ALIGNED_ENVELOPE_CERTIFICATE.md:14-16`).
  Magnitudes DESIGN.
- (i) [L1]; transport-model margins are Type I margins in disguise (I25).

#### M6. Heat-current perturbation, evolution variable and kick amplitude

- (c) δ = +7.5e−5 keeps all rows (cone margin 4.77e−6); +1e−4 gives the first
  failure at reset/support edge; −5e−4 relieves (5.72e−4)
  (`STAGE2_BETA075_PRINCIPAL_SYMBOL_SENSITIVITY.md:32-64`). Rapidity ψ
  evolution passes +1e−4 where the raw heat ratio fails
  (`STAGE2_BETA075_REDUCED_TRANSPORT_EVOLUTION_PILOT.md:13-20`). Impulse kick
  at 5× observed fails (1.434) while the same source spread in time passes
  (0.850) (`STAGE2_BETA075_RAPIDITY_BUDGET_DIAGNOSTIC.md:28`;
  `STAGE2_BETA075_SUPPORT_SOURCE_DYNAMICS.md:25-29`).
- (e) I25: the heat characteristic closes exactly as the Type I margin closes
  (minimum cone margin 7.881e−5 and transport margin 7.983e−5 on one row).
  Rapidity headroom is near-additive in ψ (ψ₀+Δψ_max ≈ 6.9–7.25 ≈ ½ln(2/ε),
  INVENTORY arithmetic on `STAGE2_BETA075_RAPIDITY_BUDGET_DIAGNOSTIC.md:28-83`).
- (i) [L1].

#### M7. Support-edge source reshaping (smoothing vs amplitude cap)

- (c) Smoothing 2.0756 → 1.9997 (fails); cap 0.95 gives 0.289/0.373 but
  moves the large-amplitude failure to other phases (1.445, 1.256, 1.047) and
  scales one slice to 9.3% (`STAGE2_BETA075_SUPPORT_EDGE_SOURCE_RESHAPING.md:61-114`).
- (h) Smoothing does not repair amplitude overdrive. (i) [L1].

#### M8. 3+1 "backreaction" proxy scenarios

- (a) No Einstein solve; the driver is the residual ∇·(T_endpoint + T_support)
  propagated with scenario multipliers ≤1.0588
  (`STAGE2_BETA075_FIRST_ORDER_3P1_COUPLING.md:61-66`;
  `STAGE2_BETA075_MODERATE_3P1_V5_CAPSTONE.md:58`); the capstone was demoted to
  a "light local off-axis/backreaction proxy" (`STAGE2_BETA075_3P1_BACKREACTION_CAPSTONE.md:7-14`).
- (c) Peak instantaneous driver 1.652 against a 1.75 gate
  (`STAGE2_BETA075_MODERATE_3P1_V5_CAPSTONE.md:48-75`).
- (i) [L1]; not a backreaction computation.

#### M9. Source-role partition and composite ansatz (promoted pair, May 19)

- (a) Oracle assignment of demand to roles A–I by channel, stage, region and
  live flag (`STAGE2_COMPONENT_SOURCE_LEDGER_PROMOTED_PAIR.md:20-47`).
- (c) Coverage: radial null 0.990/0.996, radial pressure 0.724/0.735, current
  0.342/0.400, angular 0.963/0.954 (`:57-58`); live residuals zero by
  construction, "should not be read as physical closure" (`:77-80`). Fitted
  sector ratios: infrastructure p_l/ρ = −1.002 (string-cloud-like), live
  trim p_l/ρ = −1.148 with p_Ω/ρ 3.095 → 4.029 for radius 2.05
  (`STAGE2_COMPOSITE_SOURCE_ANSATZ_PROMOTED_PAIR.md:60-65`).
- (e) INVENTORY DERIVATION (identities extraction): from the fitted means, the
  distributed current sector H is flux-dominated (Type IV) and a
  near-saturated string cloud flips to Type IV with a tiny current (I3). The
  "conserved string cloud" is the geometric W-term (I12).
- (i) Pre-beta075 geometry; type untested in the reports.

#### M10. Nonminimal scalar source model (profile × φ₀ × ξ)

- (c) 100 rows; best radial-null coverage 0.0072 (compact) and 0.0051
  (radius 2.05) at ξ = 1; demand/supply top-20 overlap 0/20 (the scalar's
  negative T_kk lands in reset rows, demand sits in entry/catch rows); a
  localized fixed-metric solve reaches 7.77e−6 coverage
  (`STAGE2_PROMOTED_PAIR_SCALAR_KILL_SCREEN_PROGRESS.md:49-70, 87-88, 142-171, 228-232`).
- (e) Coverage failure measured; the minimally coupled limit is excluded by
  I23. (i) Pre-beta075.
