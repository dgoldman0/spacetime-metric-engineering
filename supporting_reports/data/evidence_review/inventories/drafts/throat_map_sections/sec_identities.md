## 5. General identities for spherical warped products

Status labels:

- **DERIVED-IN-REPO**: the report states the relation and derives it or
  checks it against analytic controls.
- **STATED**: asserted in a report or docstring without derivation; standard GR.
- **INVENTORY DERIVATION**: derived for this inventory from the repo's
  definitions; not stated in any report. Needs a textbook derivation before use.

Notation: the book's class is ds² = −α²dσ² + A(dl+βdσ)² + B dΩ², R=√B.
`COUPLED_SOURCE_ROLE_AUDIT.md` and `ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md`
write **A for the lapse** in a static proper-distance gauge
(ds² = −A²dt² + dl² + R²dΩ²); `LE_COUPLED_RESET_SOURCE_ATTEMPT.md` and
`LE_RESET_INVERSE_SEARCH.md` use areal gauge (r, f=1−2m/r) and write B for a
string density. The identities below keep each source's notation and state it.

Several of the cleanest statements (I1–I4) were written on 2026-09-23 in
`CONSTANT_RADIUS_TRACK.md` and `adm_harness/warped_product.py`, after the era
closed. They are exact for every metric of the class, so they govern every
throat-era geometry retroactively.

### 5.1 Time-dependent class identities (any α, β, A, B)

**I1. Warped-product Einstein tensor.** For g = g_ab dx^a dx^b + R²dΩ² on the
(σ,l) quotient,
"G_ab = −(2/R)∇_a∇_bR + g_ab[(2/R)□R + ((∇R)²−1)/R²], G^θ_θ = □R/R − K"
(`CONSTANT_RADIUS_TRACK.md:145-149`; `toolkit/adm_harness_cli/adm_harness/warped_product.py:3-7`).
K is the Gaussian curvature of the quotient metric. STATED; validated on
Ellis, a dust cosmology and Painlevé–Gullstrand Schwarzschild
(`CONSTANT_RADIUS_TRACK.md:154-158`).

**I2. Radial null energy is the null Hessian of the areal radius.**
"every radial null vector k satisfies 8πT(k,k) = G(k,k) = −(2/R) k^a k^b ∇_a∇_b R"
(`CONSTANT_RADIUS_TRACK.md:29-35`; `warped_product.py:9-10`). For an affinely
parametrized radial null ray this reads 8πT(k,k) = −(2/R) d²R/dλ²: the radial
NEC fails exactly where R is convex along affine radial null rays (INVENTORY
DERIVATION). Consequence: lapse, shift and radial stretch reach the radial
null energy only through the null geodesics along which R is differentiated.

**I3. Radial discriminant = product of the two radial null energies.**
"With k±=n±e_ℓ, the orthonormal radial block has ρ+p_ℓ=½[T(k+,k+)+T(k−,k−)] and
j_ℓ=¼[T(k−,k−)−T(k+,k+)], so Δ_rad=(ρ+p_ℓ)²−4j_ℓ²=T(k+,k+)T(k−,k−). The
demanded tensor is therefore Type IV exactly where the outgoing and ingoing
radial null energies have opposite signs … A static geometry has equal values
and a zero current; time dependence acting on a varying radius separates them."
(`CONSTANT_RADIUS_TRACK.md:37-49`). DERIVED-IN-REPO. The same discriminant
D=(ρ+p_l)²−4j_l² with "D < 0: flux-dominant Type-IV block" is the May-era
criterion (`STAGE2_BETA075_ENDPOINT_SOURCE_CLASS_SCREEN.md:49-57`). Under a
radial boost T(k±) rescale by e^{±2η}, so the verdict is frame-invariant.
Rest-frame quantities of a Type I block:
"ρ_rest=(ρ−p_l+sgn(ρ+p_l)√((ρ+p_l)²−4j_l²))/2" (`LE_BOUNDARY_GATE_PREFLIGHT.md:70-72`),
"v=2j_l/(ρ+p_l+sgn(ρ+p_l)√((ρ+p_l)²−4j_l²))" (`LE_CLASSIFIER_REPAIR.md:19-21`).
Combining I2 and I3: **Type IV demand requires time dependence acting on a
region where R varies** (both radial null Hessians must differ in sign).

**I4. Constant areal radius gives an exact, boost-invariant string cloud.**
"Where R is constant its Hessian vanishes, so the radial block is exactly
ρ=−p_ℓ=1/(8πR²), j_ℓ=0 … p_Ω=(1/8π)(□R/R−K)=−K/8π" and "A string's worldsheet
stress is invariant under boosts along the string"
(`CONSTANT_RADIUS_TRACK.md:77-94`). Angular null energy on such a track:
"ρ+p_Ω=(1/8π)(1/R_b²−K)" (`CONSTANT_RADIUS_TRACK.md:288-290`). DERIVED-IN-REPO
from I1; unit-tested (`tests/test_warped_product.py:55-66`, per the
identities extraction). Consequence: holding R constant moves every
two-dimensional (α, β, A) dynamic into the angular pressure, whose NEC fails
where K > 1/R².

**I5. Radial null speeds and cone tilt.** "`dl/dsigma = -beta +/- alpha/sqrt(gamma_ll)`"
(`STAGE2_BETA075_REDUCED_PRINCIPAL_SYMBOL_HYPERBOLICITY.md:17`;
`STAGE2_HORIZON_REACHABILITY_AND_CAUSAL_GUARD_REPORT.md:81-82`), with the
stationary-vector test "g_sigma_sigma = -alpha^2 + gamma_ll beta^2"
(`STAGE2_GZ_OBSTRUCTION_SCREEN.md:22-25`). INVENTORY DERIVATION:
v₊v₋ = g_σσ/A and v₊+v₋ = −2β, so g_σσ ≥ 0 ⇔ |β| ≥ α/√A ⇔ both radial null
branches move in the same coordinate direction. This marks an ergo-like
region (no observer can hold fixed l); it is a horizon only if the v=0
surface bounds a region null rays cannot leave, which the escape audits
refuted for this design (`STAGE2_HORIZON_ESCAPE_REFINED_BETA075_CORE.md:151-167`).

**I6. Packet (occupant) norm and clock.** For a radial worldline dl/dσ = v:
`packet_norm = -alpha*alpha + gamma_ll*(vcoord + beta)**2`
(`toolkit/adm_harness_cli/adm_harness/source_ledger.py:1550`). Timelike ⇔
v₋ < v < v₊ (I5); the proper-time rate is dτ/dσ = √(−norm). A comoving shift
v+β=0 gives norm = −α² and dτ/dσ = α (INVENTORY DERIVATION). Only the sign is
frame-free; the magnitude scales with α², so the reported "max live packet
norm" values are not comparable margins across designs with different lapse.

**I7. Shift re-match algebra.** The collar edit δβ = −g·W·(v+β)
(`source_ledger.py:1522-1526`; `STAGE1_PACKET_BETA_REMATCH_TEMPORAL_PROBE.md:29`)
gives v+β_new = (1−gW)(v+β_pre): causal margin improves for 0 < gW < 2 and is
maximal at gW = 1 (INVENTORY DERIVATION). The margin is bought pointwise and
algebraically; its price appears only through derivatives of β in G.

**I8. Coordinate-normalized null energy carries α².** With k^σ = 1,
"Tkk_plus / alpha^2 = rho_H + p_l - 2 j_l; Tkk_minus / alpha^2 = rho_H + p_l + 2 j_l"
(`STAGE1_CHANNEL_CAUSE_LEDGER_FINDINGS.md:36-41`). "The coordinate `Tkk` peak
is large because the local metric scale is large, not because the local ADM
pieces are huge" (`STAGE1_CURRENT_CANDIDATE_ALGEBRA_LEDGER.md:203`). The
throat-era `neg_Tkk_radial` burden is this coordinate quantity integrated with
weight √A·B (`source_ledger.py:1888, 2436`). Any lapse knob rescales it by α²
at fixed orthonormal stress; the reports never separate that share.

**I9. Uniform slowdown (rate κ) cannot cure Type IV at an enthalpy zero.**
With σ=κt, α and γ fixed at matched phase and β→κβ,
"j_κ=κj_1 … X_κ=X_0+κ²(X_1−X_0), X∈{ρ,p_ℓ,p_Ω}" and at a spatial zero of the
static enthalpy h_0, "Δ_κ=(ρ_κ+p_{ℓ,κ})²−4j_κ²=κ²(κ²h_2²−4j_1²)", threshold
"κ_c=2|j_1|/|h_2|. Thus the static limit can be Type I while every nearby
evolving member still contains Type IV stress" (`LE_BOUNDED_METRIC_REPAIR.md:101-136`).
DERIVED-IN-REPO; exact for the uniform-rate family of any metric of the class.
Measured: |Δ| ∝ κ², |Im λ| ∝ κ, layer width ∝ κ (`LE_BOUNDED_METRIC_REPAIR.md:173-192`).

**I10. Null expansions of the symmetry spheres (proxy form).**
"R = sqrt(gamma_omega); v_+/- = -beta +/- alpha / sqrt(gamma_ll);
theta_+/- = 2 (d_s R + v_+/- d_l R) / R" (`STAGE2_NULL_EXPANSION_PROXY.md:26-30`),
along the coordinate null directions K± = α(n ± e_l); only the sign is
invariant, and the report calls it "not a theorem-level trapped-surface
calculation" (`STAGE2_NULL_EXPANSION_PROXY.md:12-14`). INVENTORY DERIVATION:
θ₊θ₋ = −(4α²/R²)(∇R)², so both expansions share a sign only where ∇R is
timelike; with ∂_σR = 0 that requires |β|√A > α on a flank with ∂_lR ≠ 0.
Constant R gives θ± ≡ 0 (`CONSTANT_RADIUS_TRACK.md:253-255`).

**I11. Radial bundle focusing ignores the areal radius.** INVENTORY
DERIVATION from I5: d(δl)/dσ = (∂_l v±)δl = (−∂_lβ ± ∂_l(α/√A))δl, independent
of B. Measured agreement: areal smoothing changed bundle width by 0.989×, β
smoothing by 1.65–1.94×, γ_ll smoothing made it worse (0.354×)
(`STAGE2_COLLAR_MITIGATION_SCREEN.md:93-99, 135-137`).

**I12. Areal flux of a radial string cloud.** For T_ab = −μ g_ab on the
quotient with p_Ω = 0, ∇·T = 0 ⇔ ∂_a(μR²) = 0 (INVENTORY DERIVATION; static
form asserted: "If separately conserved and static, this ideal pattern
requires I∝R^{-2}. A varying flux or termination requires angular stress or
exchange", `COUPLED_SOURCE_ROLE_AUDIT.md:70-74`). From I1 the geometry's own
flux is 8πR²(ρ−p_l)/2 = 1 − (∇R)² − R□R, i.e. ≈1/(8π)=0.039789 where R is
nearly constant. The Stage II fitted flux Φ = 0.039772
(`STAGE2_RADIAL_STRING_CLOUD_ENDPOINT_CROSSWALK.md:72`) is this geometric
W-term, not an independent matter finding; `CONSTANT_RADIUS_TRACK.md:346-348`
later makes it exact.

**I13. Join regularity sets stress growth.** A metric function with a d^p
cusp has second derivatives ∝ d^{p−2}: "The metric is continuous with a
square-root cusp there. Its second radial derivative grows as d^{−3/2}"
(`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:167-169`), measured as ×2^{3/2} per
halving (`:179-180`) with an unbounded absolute stress integral (`:194-199`).
A first-derivative jump gives a sampled h⁻¹ surface term (`:185-188`); "C2
matching permits first-order curvature convergence at the exact joins"
(`LE_RECEIVER_C2_REPAIR_ATTEMPT.md:80-81`); C∞ primitives converge at the
scheme order (`CONSTANT_RADIUS_TRACK.md:193-196`). Exception measured: a
temporal slope jump in a shell cap gave finite sampled G
(`LE_BOUNDED_METRIC_REPAIR.md:52-55`). C1-only joins were never tested.

**I14. Lapse-only dynamics carry no energy flux.** "the momentum constraint
makes the Eulerian energy flux vanish wherever the spatial metric is static
and the shift is zero, whatever the lapse does" (`AXIAL_TRACK.md:228-230`,
post-era; general ADM). Measured corollary in this era: static support with
moving packet windows and zero shift contributed 236 Type IV points against
842 for the full geometry (`CONSTANT_RADIUS_TRACK.md:59-65`).

**I15. Divergence does not fix type.** "∇_μT^{μν}=J^ν … allows addition of any
divergence-free tensor, so it leaves the support tensor's algebraic type
underdetermined" (`LE_BOUNDARY_GATE_PREFLIGHT.md:137-145`).

### 5.2 Static identities (β=0, time-independent; proper-distance gauge, lapse A)

**I16. Static source decomposition.** For ds² = −A²dt² + dl² + R²dΩ²:
"X=A''/A, Y=A'R'/(AR), Z=R''/R, W=(1−R'²)/R²" and
"8π(ρ,p_r,p_t)=W(1,−1,0)+Z(−2,0,1)+Y(0,2,1)+X(0,0,1)"
(`COUPLED_SOURCE_ROLE_AUDIT.md:79-98`); "the displayed pieces acquire physical
component meanings only through a source model and its exchange equations"
(`:99-102`). Checked against flat space, cylinder, Ellis and de Sitter static
patch (`toolkit/adm_harness_cli/scripts/audit_coupled_source_roles.py:33-56`).
Roles: W = finite-radius tension, null-neutral; Z = opening, the only term
in 8π(ρ+p_r) = −2Z + 2Y besides clock–radius overlap; X = clock curvature,
angular only; Y = clock–radius overlap, radial pressure and angular.

**I17. Tension and opening are separate duties at a throat.** "At a smooth
minimum of radius, R'=0, the radial pressure is −1/(8πR_0²) … A strict minimum
also has R''>0, giving ρ+p_r=−R''/(4πR_0)<0. Tension and opening are therefore
different requirements even at the same location"
(`COUPLED_SOURCE_ROLE_AUDIT.md:104-110`). General static radial null energy
from I16: 8π(ρ+p_r) = −2(R'' − A'R'/A)/R (INVENTORY DERIVATION). Unit lapse:
"both radial null energies equal −R''/(4πR)" (`CONSTANT_RADIUS_TRACK.md:94-95`).

**I18. Flare-out (opening) identity and bound.** "(R'/A)'=−(4πR/A)(ρ+p_ℓ), so
widening a uniform track from R'=0 to R'/A=1 requires an integrated radial
null deficit of at least one per end, a uniform continuation requires none,
and a closing cap decreases R'/A with non-negative ρ+p_ℓ"
(`CONSTANT_RADIUS_TRACK.md:327-334`; also `COUPLED_SOURCE_ROLE_AUDIT.md:170-172`).
Measured opening 2.000001 on a two-ended slice (`CONSTANT_RADIUS_TRACK.md:325-326`).
Transition width sets only the peak: −0.118, −0.058, −0.028 at widths 0.75,
1.5, 3 (`CONSTANT_RADIUS_TRACK.md:183-185`), i.e. peak ∝ 1/width.

**I19. Clock identity.** "(R²A')'=4πR²A(ρ+p_r+2p_t). A strict interior lapse
maximum needs a negative value of this source there. Positive potential energy
can provide that sign while saturating both null conditions"
(`COUPLED_SOURCE_ROLE_AUDIT.md:113-119`). A clock maximum costs a strong-energy
(ρ+p_r+2p_t) violation, not a null-energy violation.

**I20. Static conservation.** "p_r'+(A'/A)(ρ+p_r)+2(R'/R)(p_r−p_t)=0"
(`COUPLED_SOURCE_ROLE_AUDIT.md:129-131`): ending a radial load couples angular
stress, clock gradient and radial enthalpy at every interface (`:133-136`).

**I21. Ellis throat, closed form (ultrastatic, α=A=1, β=0, c_Ω=1).**
"ds²=−dσ²+dl²+(l²+a²)dΩ² … ρ=p_l=−a²/(8π(l²+a²)²), j_l=0, p_Ω=a²/(8π(l²+a²)²)"
(`LE_BOUNDARY_GATE_PREFLIGHT.md:159-171`; matches samples within 8.02e-11,
`:173`). Type I, negative energy, |l|⁻⁴ tail whose two-ended norm integral
beyond L is "2a arctan(a/L) ∼ 2a²/L" (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:235-253`).
With a constant angular jacket c_Ω ≠ 1 the far tail approaches a string cloud
ρ ≈ −p_l ≈ (1−c_Ω²)/(8πR²) (INVENTORY DERIVATION).

**I22. Static geometries are Type I in the radial block.** From I3 (j=0 in the
static frame). Measured: all 4,504 matched static-control samples Type I while
every active phase contains Type IV (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:133-144`).
Consequence: a static surrogate cannot detect the Type IV layer.

**I23. Canonical fields supply no null deficit.** Static canonical condensate:
"(ρ,p_r,p_t)=(K+D+V+E, K+D−V−E, K−D−V+E) … radial and angular null stresses are
2(K+D) and 2(K+E)" (`COUPLED_SOURCE_ROLE_AUDIT.md:193-197`). A minimally
coupled scalar's radial block "is boost-diagonalizable and the signs of
rho+p_l and p_l-pOmega are tied to the scalar kinetic sign"
(`STAGE2_BETA075_MATTER_ACTION_FEASIBILITY_WORKLOG.md:79-81`), so it is never
Type IV. Components with non-negative null stress cannot reduce the negative
null requirement (`COUPLED_SOURCE_ROLE_AUDIT.md:15-17`).

### 5.3 Algebraic-type and source-model relations

**I24. The minimal Type I regulator changes the source.** "minimal regulator =
max(0, 2 |j_l| - |rho + p_l|)", split "delta rho = 0.5 sign(rho+p_l) regulator;
delta p_l = 0.5 sign(rho+p_l) regulator" (`STAGE2_BETA075_ENDPOINT_CURRENT_REGULATOR_SCREEN.md:56-66`).
Adding it gives |ρ+p_l| = 2|j_l|, i.e. D=0 exactly ("exactly luminal at safety
factor 1.00", `STAGE2_BETA075_REGULATED_MEDIUM_ADMISSIBILITY_AUDIT.md:100-101`).
The regulated tensor is a different T from the Einstein demand.

**I25. Heat-mode speed equals the Type I margin.** "v_q = 2 j_l / |rho + p_l| =
tanh(psi); h_reg = 1 - v_q^2 >= 0" (`STAGE2_BETA075_SOURCE_FAMILY_EQUATION_PACKAGE.md:69-70`).
D = (ρ+p_l)²(1−v_q²) (INVENTORY DERIVATION): a medium realizing a near-Type-II
radial block has a near-luminal heat characteristic. Measured coincidence:
minimum cone margin 7.881e-5 and transport margin 7.983e-5 on the same row
(`STAGE2_BETA075_REDUCED_PRINCIPAL_SYMBOL_HYPERBOLICITY.md:43`;
`STAGE2_BETA075_RAPIDITY_BUDGET_DIAGNOSTIC.md:28`).

**I26. Boosted infrastructure preserves the discriminant.**
"j_b=J c²h_b²/(J²+c²h_b²), c=2v_max/(1−v_max²)", D=h_b sinh²ψ; this "preserves
the infrastructure's radial discriminant" (`LE_RESET_INVERSE_SEARCH.md:115-125`).

**I27. Areal-gauge mass relations** (metric −α²dt²+dr²/f+r²dΩ², f=1−2m/r):
"m_b=(r/2)[1−(∂_ℓ r)²/γ_ℓℓ]", "∂_r log α=(m+4πr³P_r)/(r(r−2m))",
"∂_t m=−4πr²α√f J" (`LE_COUPLED_RESET_SOURCE_ATTEMPT.md:103-117`). Consequence
measured there: adding positive-enthalpy material to remove Type IV consumes
the f>0 mass allowance (required δm ≈ 1.433 against 0.533 available,
`LE_COUPLED_RESET_SOURCE_ATTEMPT.md:197-205`).

**I28. Onset obstruction (registered families).** A prescribed geometric
acceleration with J=j_*u^{n−1} demands angular stress at order u^{n−2} while
initially empty moving material supplies it at u^{2n−2}
(`LE_RESET_INVERSE_SEARCH.md:389-421`); scoped "for these source families and
boundary conditions" (`:419-421`).

### 5.4 Source-physics identities (independent of the throat)

**Q1. Radial 1+1 conformal channels (spherically averaged).**
"ρ_Q = ηc/(4πR²)[−π/(24L²A²) + (2a''+a'²)/(24π)], p_r,Q = ηc/(4πR²)[−π/(24L²A²) − a'²/(24π)],
p_t,Q = 0" with L=∫dl/A, a=log A (`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:80-85`).

**Q2. Anomaly lock.** "ρ_Q−p_{r,Q}=ηc/(48π²R²)(a''+a'²). Consequently
shortening a cavity increases its negative radial-null stress while preserving
this independent tensor constraint" (`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:128-134`).

**Q3. Reflector reaction and subdivision scaling.** F = −4πR²[p_r]
(`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:103-113`); outer end loads ∝ (compartment
count)², internal forces balance (`:115-117`); "fourfold shortening multiplies
the local Casimir part by 16", Σc_jL_j invariant under repartitioning
(`C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:162-166`).

**Q4. Longitudinal supply bound.** With W=exp[−(R²−R₀²)/2k], the 1+1 source
must satisfy C∫W/A² dl − (∫WRR''/k dl + [Wa']) = (4π/k)∫WR²H_rem dl ≥ 0
(`COUPLED_REORIENTATION_INVESTIGATION.md:209-218`); "A global rescaling of time
leaves the source and the bound unchanged" (`:260-262`); AdS₂ positive control
gives exactly 4 (`:304-307`).

**Q5. Conformal scalar on a cylinder and the curvature-coupling logarithm.**
"(ρ,p_r,p_t) = ηN/(2880π²R⁴)(−2log(R/a₀), 2log(R/a₀), 1−2log(R/a₀))"
(`C1_ANGULAR_SCALAR_INVESTIGATION.md:58-61`), angular-null negative for
log(R/a₀) > 1/4 (`:68-69`); T(ℓ₀) = T(1) − 2(ℓ₀−1)H
(`C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:125`); a subtraction-convention
change "supplies no additional stress" (`:143-150`).

**Q6. Boundary-state response and holding cost.** Dirichlet end:
(Δρ,Δp_r,Δp_t) = Δb(1/6,1/2,−1/6); held product-cylinder interaction
d|F|/|E| = 1 + zK₀(z)/K₁(z) > 1, so E_int + d|F_int| > 0 for a DEC-obeying
direct static support (`C1_ANGULAR_NORMALIZATION_AND_BOUNDARY_RESPONSE.md:199-201, 253-268`).

**Q7. Planar EM Casimir cells.** C = ηπ²/(720d⁴); independently held cells need
holder energy ≥ 3(C_r+2C_t), complete cells ≥ 2(C_r+2C_t)
(`COUPLED_REORIENTATION_INVESTIGATION.md:129-145`).

**Q8. Shared-field pair cross term.** u_E = (Q_L²+Q_R²)/2R⁴ + Q_LQ_R/R⁴
(`C1_FINITE_MODULE_PAIR_SCREEN.md:56-57`).

**Q9. Scalar-mirror proximity co-scaling.** h_I and h_χ both ∝ η/a³ at fixed
optical strength and relative thickness (`NARROW_CURVED_CAVITY_EVALUATION.md:82-87`).

**Q10. Capacitor shells.** σ = (√f_in − √f_out)/(4πr); U_E/(M_in+M_out) ≤
2(b−a)/(b+a) (`CHARGED_CAPACITOR_CONSTRUCTION.md:56-59, 116-121`).

**Q11. Magnetic confinement.** B²/8π > P_γ + P_e±
(`STORAGE_CONTAINMENT_LITERATURE_REVIEW.md:57-59`); sleeve virial
E_sleeve ≥ 2E/(3k(1+πa/L)) (`MAGNETIC_GEOMETRY_COMPARISON.md:182-183`).

**Q12. Oriented ensembles.** T^Maxwell = u(δ−2bb), T^sheet = −u(δ−aa),
T^string = −uss; H ≤ 2kE_material (`CONTAINMENT_ENSEMBLE_ROLE_AUDIT.md:63-66, 160-164`).

**Q13. Scale invariance of module power.** C_J/δ_s ∝ c⁵/G independent of L_g;
C_Jδ_s/ħ ∝ (L_g/ℓ_P)² (`RAIL_STORAGE_AND_INTERFACE_STATUS.md:111-133`).
