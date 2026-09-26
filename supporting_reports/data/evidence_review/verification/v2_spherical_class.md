# V2. Spherical warped-product identities: independent verification

Verification of the general identities for spherical warped products in
`inventory/knobs_throat_era.md` §5 (I1–I28) and of their one-space restatement,
`inventory/knobs_one_space.md` §3.1, I24. Everything below comes from
`v2_spherical_class.py`. That script is written from scratch; no project code
was imported or adapted, and project reports were read only for the exact
statements.

**Bottom line.** 170 of 170 checks pass. Every identity is correct as algebra
or analysis. Eleven items need a corrected or added hypothesis, a scope
restriction, or a design label before they enter the book:

- I7, I11, I13, I16, I17, I18, I19, I23 and I24 carry corrections or added
  hypotheses;
- I25 has a model-specific physical reading;
- I28 is specific to its registered source families.

The one-space I24 agrees with the throat-era statements. It inherits one
notation hazard: A denotes the lapse there, while class S uses A for γ_ll.

Four results emerged during verification that the book can use directly:

- I18 is I2 integrated along a radial null ray, and it generalizes to
  time-dependent geometries.
- Every stationary region of class S is Type I, whether static or
  homogeneous.
- The shift enters the Eulerian tensor undifferentiated only through the
  normal derivative.
- The Einstein tensor of class S has an exact derivative-weight structure,
  which fixes the join-regularity rule.

---

## 1. Notation, gauges and conventions

**Book conventions** (`05_STRUCTURE.md`):

- signature (−,+,+,+) and G = 8πT;
- MTW Riemann tensor, R^a_{bcd} = ∂_cΓ^a_{db} − ∂_dΓ^a_{cb} + Γ^a_{ce}Γ^e_{db} − Γ^a_{de}Γ^e_{cb}, and R_{bd} = R^a_{bad};
- Eulerian quantities ρ = T(n,n), j_i = −T(e_i,n), p_i = T(e_i,e_i).

**Class S.** ds² = −α²dt² + A(dl + β dt)² + B dΩ², where α, β, A, B are
functions of (t,l), α, A, B > 0, and R = √B.

- Quotient metric: g_ab dx^a dx^b = −α²dt² + A(dl + βdt)², with a, b ∈ {t, l}.
- ∇ is its Levi-Civita connection, □R = g^{ab}∇_a∇_bR and (∇R)² = g^{ab}∂_aR∂_bR.
- K is the Gaussian curvature of g_ab, defined by ²R_ab = K g_ab. It is
  positive on dS₂ (checked with Nariai dS₂×S²).

**Normal frame.**

- n = α⁻¹(∂_t − β∂_l), e_l = A^{−1/2}∂_l, e_θ = B^{−1/2}∂_θ.
- Radial null vectors k± = n ± e_l, so T(k±,k±) = ρ + p_l ∓ 2j_l.
- Radial enthalpy h = ρ + p_l and discriminant Δ = h² − 4j_l².
- Radial null speeds v± = −β ± α/√A.

**Static gauge (I16–I20).** ds² = −N²dt² + dl² + R²dΩ², with l proper radial
distance and ′ = d/dl.

> **Notation hazard.** The reports (`COUPLED_SOURCE_ROLE_AUDIT.md`,
> `CONSTANT_RADIUS_TRACK.md`) and one-space I24 write this lapse as **A**,
> which class S uses for γ_ll.

Every static result below is also given in an arbitrary radial gauge
ds² = −N²dt² + A dl² + R²dΩ², with s the proper radial distance and d/ds = A^{−1/2}∂_l.

**Areal gauge (I27, I28).** ds² = −α²dt² + dr²/f + r²dΩ², with f = 1 − 2m/r
and zero shift. Time dependence is allowed.

## 2. Method and reproducibility

**Two independent engines compute the Einstein tensor from scratch**
(Christoffel → Ricci → G, MTW signs).

- *Jet engine (general identities).* Each field and each partial derivative
  up to order 4 is an independent symbol, and ∂_t, ∂_l act as total
  derivatives through the chain rule. A pointwise differential identity holds
  for all smooth fields iff it holds on all jets, so jet checks prove the
  identities rather than sample them. The full class-S tensor builds in about
  2 s.
- *Explicit engine (examples).* Direct `sympy.diff` of explicit metrics. It
  serves the validation spacetimes, the field-theory sources and the areal
  gauge.

**Every jet identity is checked twice:**

- (a) exact symbolic reduction of the difference to zero (`sympy.cancel`);
- (b) exact evaluation of the difference at 3–4 random rational jets
  (Schwartz–Zippel test). Positive fields are drawn as perfect squares, so
  the radicals stay rational.

A negative control shows that test (b) discriminates: the Ricci tensor alone
fails the divergence test, and its divergence equals ∂R/2 exactly.

**Numerical parts** use mpmath at 30 significant digits (20 for the geodesic
integration):

- quadratures of the opening integrals;
- finite-difference sampling at joins;
- RK4 integration of a radial null geodesic.

**Performance.** No symbolic step came near the 15-minute limit; the full run
takes 20–90 s depending on machine load.

**Run.**

```
cd T/verification
nice -n 10 env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 v2_spherical_class.py
```

- Exit status is 0 iff all checks pass. The log of the recorded run is
  `v2_run.log`: 170/170 PASS, Python 3.13.7, sympy 1.14.0, mpmath 1.3.0.
- Seeds are fixed, and symbols are sorted before random substitution.
  Two runs, one with `PYTHONHASHSEED=12345`, produce identical output
  apart from timings.
- Optional arguments `step0 td static x24` run single sections.
- Checks labelled CORRECTION confirm a counterexample to an inventory
  statement, so they pass when the counterexample holds.

## 3. Step 0: validation of the engines (18/18)

| Control | Result |
|---|---|
| Round S² of radius r₀ | Ricci scalar +2/r₀² (MTW sign) |
| Schwarzschild, Painlevé–Gullstrand (α=1, β=√(2M/r), A=1, B=r²) | G_μν = 0 in the explicit engine; ρ = j = p_l = p_Ω = 0 in the jet engine (non-zero shift) |
| FRW, generic a(t), k = +1, 0, −1 | 8πρ = 3(ȧ²+k)/a², 8πp = −2ä/a − (ȧ²+k)/a², isotropic, j = 0 |
| FRW dust, a = t^{2/3} | ρ = 1/(6πt²), p = 0 |
| Ellis throat (α = A = 1, B = l²+a²) | ρ = p_l = −a²/(8π(l²+a²)²), p_Ω = −ρ, j = 0 (the I21 closed form) |
| Morris–Thorne, e^{2Φ}, 1/(1−b/r) | ρ = b′/(8πr²); τ = −p_r = [b/r − 2(r−b)Φ′]/(8πr²); p_t = (r/2)[(ρ−τ)Φ′ − τ′] − τ |
| Morris–Thorne throat, b(r₀) = r₀ | τ₀ = 1/(8πr₀²); ρ + p_r = (b′(r₀) − 1)/(8πr₀²), negative under flare-out b′(r₀) < 1 |
| Reissner–Nordström; de Sitter static patch | ρ = −p_r = p_t = Q²/(8πr⁴); ρ = −p = 3H²/(8π) |
| Random polynomial class-S metric, rational point | jet engine = explicit engine to 60 digits (ρ, j, p_l, p_Ω) |
| Contracted Bianchi identity, general class S | ∇_μG^μ_ν = 0 (third-order jets); Ricci-only negative control fails, as it must |

---

## 4. Time-dependent class identities (I1–I15)

### I1. Warped-product Einstein tensor — VERIFIED

**Statement (theorem).** Let g = g_ab dx^a dx^b + R² dΩ², where (Q, g_ab) is
a Lorentzian 2-manifold and R > 0 is C² on Q. This covers every spherically
symmetric metric, and class S in particular. Then

- G_ab = −(2/R)∇_a∇_bR + g_ab[(2/R)□R + ((∇R)² − 1)/R²];
- G_aA = 0;
- G^A_B = δ^A_B(□R/R − K).

**Method.** The 4D jet tensor with arbitrary α, β, A, B is compared with the
quotient formula, component by component: tt, tl, ll, θθ, φφ and the mixed
components.

**Proof sketch.** Use the warped-product (O'Neill) Ricci formulas for
Q ×_R S² with unit-sphere metric γ:

- Ric_ab = K g_ab − (2/R)∇_a∇_bR;
- Ric_aA = 0;
- Ric_AB = [1 − R□R − (∇R)²]γ_AB.

The 4D scalar curvature is then 2K − 4□R/R + 2(1 − (∇R)²)/R². Subtracting
half of it times g gives both formulas.

**Status.** Standard: the warped-product / 2+2 spherical formalism (O'Neill,
*Semi-Riemannian Geometry* 1983, ch. 7; Gerlach & Sengupta 1979; Hayward
1996). No entry exists in the lit inventories; these anchors should be added.

### I2. Radial null energy is the null Hessian of R — VERIFIED

**Statement.** For every radial null vector k (tangent to Q, g(k,k) = 0),
8πT(k,k) = −(2/R) k^a k^b ∇_a∇_bR. Along a radial null curve with tangent k
and ∇_k k = κk:

- 8πT(k,k) = −(2/R)(d²R/dλ² − κ dR/dλ);
- for an affine parameter (κ = 0), 8πT(k,k) = −(2/R) d²R/dλ².

In Raychaudhuri form, with θ_k = 2k(R)/R: dθ/dλ = −θ²/2 − 8πT(k,k) + κθ.

- The radial NEC holds at a point iff R is concave along both affine radial
  null geodesics through it.
- α, β and A reach T(k,k) only through those geodesics and their affine
  parameter.

**Method.** The jet tensor is contracted with n ± e_l. For
k = F(∂_t + v±∂_l) with F arbitrary, the script checks nullity, the
pregeodesic property ∇_k k = κk, k(k(R)) = Hess(k,k) + κ k(R), and the
Raychaudhuri form.

**Proof sketch.** Contract I1 with k^ak^b; g(k,k) = 0 removes the trace
terms. Then k(k(R)) = k^ak^b∇_a∇_bR + (∇_k k)(R).

**Status.** Standard: the radial-null Raychaudhuri (focusing) equation of
spherical symmetry, ∂_±∂_± r ∝ −4πr T_±± in double-null form. The lit
inventories record the Raychaudhuri argument at throats (Hochberg & Visser
1998, `lit_parts/wormholes.md`; `lit_design_strategy.md` l.1345). The Hessian
form is a one-line corollary of I1.

### I3. Radial discriminant equals the product of the radial null energies — VERIFIED

**Statement.** Let T have radial orthonormal block (ρ, −j; −j, p) in the frame
(n, e_l), with k± = n ± e_l. Then:

- h = ½[T(k+,k+) + T(k−,k−)] and j = ¼[T(k−,k−) − T(k+,k+)];
- **Δ = h² − 4j² = T(k+,k+)·T(k−,k−)**.

The mixed block T^a_b has characteristic discriminant Δ, which classifies it:

| Radial block | Type |
|---|---|
| Δ > 0 | I (timelike eigenvector) |
| Δ = 0, j ≠ 0 | II (double eigenvalue, Jordan block) |
| Δ = 0, j = 0 | degenerate I |
| Δ < 0 | IV (complex pair) |

A radial boost of rapidity η maps T(k±,k±) → e^{±2η}T(k±,k±). Δ and the
signs of both radial null energies are therefore frame invariant.

For Δ > 0 and h ≠ 0:

- rest energy ρ_rest = [ρ − p + sgn(h)√Δ]/2;
- rest-frame velocity along +e_l, v = 2j/[h + sgn(h)√Δ] = tanh η, for either
  sign of h.

In spherical symmetry G_aA = 0 and the angular block is ∝ δ_AB, so the 4D
Hawking–Ellis type equals the radial type; Type III cannot occur.

**Corollaries.** With I2 and I22:

- radial Type IV ⇔ the two radial null Hessians of R have opposite signs;
- radial Type IV violates the radial NEC;
- it needs ∇∇R ≠ 0 and the absence of a non-null Killing field (genuine time
  dependence).

**Method.** Symbolic algebra; the jet tensor (T(k±,k±) = ρ + p_l ∓ 2j_l,
product identity); boost matrices; boosted rest-frame tensors for both
enthalpy signs; eigen-structure of the Δ = 0 block.

**Proof sketch.** Expand T(n ± e, n ± e). The characteristic polynomial of
T^a_b is λ² − (p − ρ)λ + (j² − ρp), with discriminant h² − 4j². Boosts rescale
the null legs by e^{±η}.

**Status.**

- Standard algebra: Γ = (ρ+p)² − 4f² is the type test of Martín-Moruno &
  Visser 2021 (lit_foundations 1.6).
- Type III is excluded by spherical symmetry (Martín-Moruno & Visser 2018,
  lit_foundations 1.4).
- The factorization into radial null energies, and its design reading, are
  new in this form.

### I4. Constant areal radius gives an exact, boost-invariant string cloud — VERIFIED

**Statement.** On an open set of Q where R = R_b is constant (α, β, A
arbitrary):

- T_ab = −g_ab/(8πR_b²) on the quotient, so ρ = −p_l = 1/(8πR_b²), j_l = 0 and
  T(k,k) = 0 for every radial null k;
- the block is identical in every radially boosted frame: a radial
  string cloud of areal flux μR² = 1/(8π);
- all two-dimensional dynamics sit in p_Ω = −K/(8π);
- ρ + p_Ω = (1/R_b² − K)/(8π), negative exactly where K > 1/R_b².

**Method.** Jet tensor with all B-derivatives set to zero. Controls: Nariai
dS₂×S² (T = −Λg/8π) and Bertotti–Robinson AdS₂×S² (ρ = −p_l = p_Ω = 1/(8πQ²)).

**Proof sketch.** I1 with ∇R = 0.

**Status.** Standard (product spacetimes M₂ × S²; string clouds, Letelier
1979). Neither anchor is in the lit inventories yet. The design reading
(constant R moves every service dynamic into p_Ω) is new in this form.

### I5. Radial null speeds — VERIFIED

**Statement.** For a radial curve with dl/dt = v:

- g(u,u) = −α² + A(v+β)² = A(v − v+)(v − v−), with v± = −β ± α/√A;
- v+v− = g_tt/A and v+ + v− = −2β;
- g_tt ≥ 0 ⇔ |β| ≥ α/√A ⇔ both radial null directions move to the same side
  in l, so no observer stays at fixed l.

This criterion refers to the chosen l-coordinate lines. Its invariant form
holds where ∂_tR = 0 and ∂_lR ≠ 0. There (∇R)² = −(∂_lR)² g_tt/(Aα²), so
g_tt > 0 ⇔ both sphere expansions share a sign (trapped or anti-trapped),
and g_tt = 0 ⇔ marginally trapped.

The inventory's remark on when a g_tt = 0 surface bounds a horizon is a
global statement about one design and lies outside an identity.

**Method.** Jets; algebra.

**Status.** Standard.

### I6. Packet norm and clock — VERIFIED

**Statement.** For u = ∂_t + v∂_l:

- norm = −α² + A(v+β)²;
- timelike ⇔ v− < v < v+ (A > 0 and the I5 factorization);
- dτ/dt = √(−norm), and the comoving choice v = −β gives dτ/dt = α.

The sign of the norm is parametrization-free. Its magnitude carries α² and
the relative speed, so comparisons across designs need dτ/dt itself.

**Status.** Standard.

### I7. Shift re-match algebra — VERIFIED; the "price" remark is FALSE (CORRECTED)

**Statement (algebra, verified).** The edit δβ = −gW(v+β) gives
v + β_new = (1 − gW)(v + β).

- |v + β_new| < |v + β| ⇔ 0 < gW < 2;
- comoving match occurs at gW = 1, where dτ/dt = α.

**Inventory remark:** "its price appears only through derivatives of β in G".
This is **false in class S**.

- **Counterexample.** α = A = 1, B = l² + 1, uniform shift b₀. This is the
  Ellis throat moving at speed b₀ in the l-coordinates, with
  ρ = (b₀²l² − 1)/(8π(l²+1)²).
- **Generic check.** ∂ρ/∂β ≠ 0 at random jets.

**Corrected statement (verified).** In the Eulerian frame, (ρ, j_l, p_l, p_Ω)
depend on the shift only through two channels:

- its spatial derivatives;
- the normal derivative n = α⁻¹(∂_t − β∂_l) of the fields and of their
  l-derivatives.

A pointwise shift edit therefore acts wherever it changes n of an l-dependent
field:

- n(R), the sphere expansion, which enters every component;
- n(∂_lβ), which enters p_Ω alone, because the quotient curvature K appears
  only there (I1).

If α, A and B are l-independent, undifferentiated β drops out of ρ, j and
p_l, but remains in p_Ω through n(∂_lβ).

**Method.** All time-derivative jets are rewritten in normal-derivative
variables (m_f = n f, ∂_l m_f, n m_f), and ∂/∂β = 0 is verified for all four
components. The counterexamples are checked at random jets and in the
explicit metric.

**Status.** The construction is design-specific. The corrected structure is
standard 3+1: K_ij = −½𝓛_nγ_ij, and the evolution term is 𝓛_nK_ij.

### I8. Coordinate-normalized null energy carries α² — VERIFIED

**Statement.** With k^t = 1, k± = ∂_t + v±∂_l = α(n ± e_l). Hence
T(k±,k±)/α² = ρ + p_l ∓ 2j_l. A lapse change rescales this coordinate null
energy by α² at fixed orthonormal stress.

**Status.** Standard.

### I9. Uniform slowdown at a static-enthalpy zero — VERIFIED

**Statement (proposition; any 3+1 metric).** Consider the family
α_κ(t,x) = α(κt,x), γ_κ(t,x) = γ(κt,x), β_κ(t,x) = κβ(κt,x), compared at
matched phase σ = κt. Let X₀ be the static control (the same α and γ at that
phase, zero shift, no time dependence). Then:

- K_κ = κK₁ and j_κ = κ j₁;
- X_κ = X₀ + κ²(X₁ − X₀) for X ∈ {ρ, p_l, p_Ω};
- j₀ = 0.

Let h₀ = ρ₀ + p_{l,0} vanish at a point, and set h₂ = h₁ − h₀. Then
Δ_κ = κ²(κ²h₂² − 4j₁²) = κ²h₂²(κ − κ_c)(κ + κ_c), with κ_c = 2|j₁|/|h₂|.

- If j₁ ≠ 0, the point is Type IV for every 0 < κ < κ_c (for every κ > 0 when
  h₂ = 0). Slowing down never removes it.
- Near a simple root with slope s = ∂h₀, the Type IV interval has width
  4κ|j₁|/|s| + O(κ²).
- |Im λ| = κ√(4j₁² − κ²h₂²)/2 at the root.

These reproduce the measured |Δ| ∝ κ², |Im λ| ∝ κ and width ∝ κ.

**Method.** Jet substitution α_{ij} → κ^i α_{ij}, β_{ij} → κ^{i+1}β_{ij}
gives exact polynomial identities in κ (class S). The root algebra is exact.

**Proof sketch.** K_ij is linear in (∂_tγ, Dβ), both ∝ κ. In the
constraints, ³R and D_iD_jα are κ-independent, while K², (∂_t − 𝓛_β)K and
the momentum constraint scale as κ², κ² and κ respectively.

**Status.** New in this form (derived in the project; exact).

### I10. Null expansions of the symmetry spheres — VERIFIED (the proxy is exact)

**Statement.** For the future-directed K± = ∂_t + v±∂_l = α(n ± e_l), the
exact expansions of the round spheres are

θ± = q^{AB}∇_A K±_B = 2(∂_tR + v±∂_lR)/R.

The reports' "proxy" is therefore the exact expansion for this normalization;
only its sign is normalization-free. Further:

- θ+θ− = −(4α²/R²)(∇R)², so both share a sign iff ∇R is timelike (trapped or
  anti-trapped spheres, 2m/R > 1 with the Misner–Sharp mass);
- with ∂_tR = 0 this requires |β|√A > α on a flank with ∂_lR ≠ 0;
- R constant ⇒ θ± ≡ 0.

A "both-shrinking" row is a future-trapped round sphere. The reports' caveat
applies only to global (event-horizon) statements.

**Method.** Covariant computation q^{μν}∇_μK_ν from the 4D Christoffels on jets.

**Status.** Standard (trapped surfaces; Hayward's trapping horizons;
Misner–Sharp). The lit inventories hold the related anti-trapped-throat work
of Hochberg & Visser 1998.

### I11. Radial light paths ignore the areal radius — VERIFIED WITH ADDED SCOPE

**Statement.** Radial null geodesics of the 4D metric are the null geodesics
of the quotient, since Γ^A_ab = 0 and Γ^a_bc contains no B. Their paths
dl/dt = v±(t,l) involve (α, β, A) only. The coordinate separation of
neighbouring rays of one family obeys

d(δl)/dt = (∂_l v±) δl + O(δl²), with ∂_l v± = −∂_lβ ± ∂_l(α/√A), independent of B.

**Added scope.** This is the in-quotient (coordinate) spreading of the rays.
The areal focusing of the same congruence is θ = 2k(R)/R, which obeys the
Raychaudhuri equation of I2, and it depends on B.

**Method.** Christoffel structure on jets; B-dependence of v± and θ.

**Status.** Elementary.

### I12. Areal flux of a radial string cloud — VERIFIED

**Statement.** Take T_ab = −μ g_ab on the quotient and T^A_B = p_Ω δ^A_B.
Then ∇_μT^μ_a = −R⁻²∂_a(μR²) − (2p_Ω/R)∂_aR, and:

- with p_Ω = 0, conservation ⇔ μR² constant on Q (static: μ ∝ R⁻²);
- a varying flux or a termination requires angular stress or exchange.

For any class-S metric, the canonical split of the radial block
T_ab = −μ g_ab + (radial null parts) has μ = (ρ − p_l)/2 and

8πμR² = 1 − (∇R)² − R□R = 2m/R − R□R,

which equals 1 where R is constant (I4).

**Method.** 4D covariant divergence with μ and p_Ω as jet fields; jet tensor.

**Status.** Standard (Letelier 1979, to be added to the lit inventories).

### I13. Join regularity — VERIFIED WITH ADDED HYPOTHESES (general rule derived)

**Structure (verified on jets).**

1. In the Eulerian frame of class S, (ρ, j_l, p_l, p_Ω) are linear in the
   second derivatives of (α, β, A, B).
2. The coefficients of those second derivatives depend on the undifferentiated
   fields only. Every other term is quadratic in first derivatives, except the
   sphere term 1/R², since each term carries total derivative weight 2 or 0.
3. Exactly three second derivatives never appear: ∂_t²α, ∂_t∂_lα and ∂_t²β.
   Lapse and shift carry no second time derivatives because they are Lagrange
   multipliers.
4. In a static region, ∂_l²A (γ_ll) never appears, because A is a radial-gauge
   function there.

**Rule.** Let one field f have a one-sided singularity f = f_reg + c d^p
across a join, with d the distance in x ∈ {t, l}, and let ∂_x²f appear with a
non-zero coefficient at the join. Then T − T[f_reg] = c p(p−1)·(coefficient)·d^{p−2} + o(d^{p−2}),
where T[f_reg] is the tensor of the regular profile:

| Exponent p | Behaviour at the join |
|---|---|
| p < 2, p ≠ 1 | stress unbounded; integrable across the join iff p > 1 |
| p = 1 (kink) | surface layer (δ); a centred-difference sample grows as h⁻¹ |
| p = 2 | bounded jump |
| p > 2 | continuous; a centred-difference sample carries an O(h^{p−2}) error (first order for a C² join) |

When ∂_x²f is absent, the leading behaviour is O(d^{p−1}) + O(d^{2p−2}). This
covers a time singularity in α or β, a mixed one in α, and a radial one in a
static γ_ll. A time kink in the lapse or shift therefore gives a bounded jump.
This explains the repo's observation that a temporal shift-slope jump in a
shell cap left G finite (`LE_BOUNDED_METRIC_REPAIR.md`:49–55).

**Added hypothesis.** The inventory's "d^p profile ⇒ stress ∝ d^{p−2}" holds
exactly when the corresponding second derivative enters the tensor.

**Method.** Four checks:

- principal-part and weight analysis of the canonical rational forms on jets;
- series for a B cusp: ρ − ρ[c=0] = −p(p−1)c d^{p−2}/(8π) for p = 1/2, 3/2, 5/2;
- centred-difference sampling of p_Ω at joins (mpmath, 30 digits), using
  ratios of successive differences per step halving;
- sampled ratios: 2^{3/2} for a B cusp d^{1/2}; 2 for kinks in B, α, β
  (spatial) and in B, A (temporal); √2 for a static γ_ll cusp; 1/2 for a C²
  join; 1/4 for smooth non-polynomial fields; bounded values for time kinks
  in α and β.

**Status.** The ingredients are standard: ADM structure (ADM 1962,
lit_foundations 6.1; Gourgoulhon 6.2) and Israel 1966 surface layers. The
explicit rule and its exceptions are new in this form.

### I14. Lapse-only dynamics carry no Eulerian energy flux — VERIFIED

**Statement.** Take an open region where ∂_tγ_ij = 0 and β = 0, or more
generally ∂_tγ_ij = D_iβ_j + D_jβ_i. There K_ij = 0, so for any lapse α(t,x):

- j_i = 0 and ρ = ³R/16π;
- the lapse enters the stresses alone;
- in class S the radial block is diagonal (Type I).

**Method.** Class-S jets with arbitrary α(t,l). A 4D spot check without
symmetry (−α(t,x,y,z)²dt² + h₁dx² + h₂dy² + h₃dz², static h_i) gives G_0i = 0.

**Proof sketch.** Momentum constraint 8πj_i = D_j(K^j_i − δ^j_iK), and the
Hamiltonian constraint.

**Status.** Standard (ADM momentum constraint).

### I15. Divergence does not fix the algebraic type — VERIFIED

**Statement.** ∇_μT^{μν} = J^ν determines T only up to a divergence-free
tensor, and divergence-free tensors of every type exist. Two examples:

- In Minkowski space, T₁ = diag(ρ,p,p,p) (Type I) and T₁ + S, with S_{01} = −j
  constant, are both divergence-free. The second is Type IV when 4j² > (ρ+p)².
- Spherically, T = (ε₊/r²)k₊k₊ + (ε₋/r²)k₋k₋ is divergence-free for every
  ε± and has T(k+,k+)T(k−,k−) = 16ε₊ε₋/r⁴. It is Type I, II or IV according
  to the signs.

**Status.** Standard (elementary).

---

## 5. Static identities and source relations (I16–I28)

### I16. Static source decomposition — VERIFIED; one role CORRECTED

**Statement (theorem).** In a static region with ds² = −N²dt² + dl² + R²dΩ²
(l proper distance, ′ = d/dl; the reports write this lapse as A), define

X = N″/N, Y = N′R′/(NR), Z = R″/R, W = (1 − R′²)/R².

Then **8π(ρ, p_r, p_t) = W(1,−1,0) + Z(−2,0,1) + Y(0,2,1) + X(0,0,1)**, with
j = 0. The same formula holds in any radial gauge with ′ = d/ds.

**What W, Z, Y, X are.**

- **W = 2m/R³.** It is the compactness of the Misner–Sharp mass
  m = (R/2)(1 − (∇R)²). By the Gauss equation of the symmetry sphere in the
  slice, W is the intrinsic curvature 1/R² minus (R′/R)². Its pattern
  (1,−1,0) is a radial string cloud.
- **Z = R″/R.** The proper radial convexity of the areal radius (the
  "opening").
- **Y = a·(R′/R).** The product of the static observers' proper acceleration
  a = N′/N and the areal expansion rate per unit proper length.
- **X = N″/N = a′ + a².** The clock curvature; it enters p_t only.
- Also W − 2Z = ³R/2, the Hamiltonian constraint 16πρ = ³R.

**Null energies.**

- 8π(ρ + p_r) = 2(Y − Z);
- 8π(ρ + p_t) = W − Z + Y + X.

**Correction.** The inventory lists W as "null-neutral". W is neutral for the
radial null energy only; it enters the angular null energy with weight +1.

**Method.** Static restriction of the jet tensor in a general radial gauge,
and in the report gauge. Controls: flat space; cylinder, 8π(ρ,p_r,p_t) =
(1,−1,0)/R_b²; de Sitter static patch R = sin(Hl)/H, N = cos(Hl); Ellis (S0).

**Proof sketch.** Static slices have K_ij = 0, so 16πρ = ³R and
8πS_ij = ³G_ij − (D_iD_jN − γ_ij D²N)/N. For dl² + R²dΩ², ³G_rr = −W and
³G_θ̂θ̂ = Z. The lapse terms follow from D_rD_rN − D²N = −2R′N′/R and
D_θ̂D_θ̂N = R′N′/R.

**Status.** The content is standard: the static spherical Einstein tensor,
Morris–Thorne 1988 in (b, Φ) form (`lit_parts/wormholes.md`, MorrisThorne1988).
The (W, Z, Y, X) packaging is new in this form.

### I17. Tension and opening are separate duties — VERIFIED; one sub-claim FALSE (CORRECTED)

**Statement.** On a sphere with R′ = 0 (any lapse, any radial gauge):

- 8πp_r = −1/R²;
- 8π(ρ + p_r) = −2R″/R.

The tension is a W-term, radially null-neutral; the opening is a Z-term. In
general, static: 8π(ρ + p_r) = −(2/R)(R″ − N′R′/N), and T(k+,k+) = T(k−,k−).

**Correction.** "A strict minimum also has R″ > 0" is **false**.
Counterexample: R = R₀ + l⁴ is a strict minimum with R″(0) = 0, and gives
ρ + p_r = −3l²/(π(R₀ + l⁴)): zero at the throat and negative on both sides.

**Corrected statement.**

- At a nondegenerate minimum (R″ > 0), ρ + p_r < 0 at the throat.
- At any strict minimum, ρ + p_r < 0 somewhere in every one-sided
  neighbourhood, by I18 on [0, ε] with R′(0) = 0 < R′(ε*).

**Status.** Standard: the throat tension τ₀ = 1/(8πr₀²) and τ₀ > ρ₀ are from
Morris–Thorne 1988. Degenerate flare-out is treated by Hochberg & Visser 1997
(`lit_parts/wormholes.md`).

### I18. Flare-out identity and the opening bound — VERIFIED WITH ADDED HYPOTHESES

**Statement (theorem).** Take a static region with lapse N > 0, R > 0 and C²
fields, with l the proper radial distance (the reports' "A" is N). Then

**(R′/N)′ = −(4πR/N)(ρ + p_r).**

In a general radial gauge this reads A^{−1/2}∂_l(∂_lR/(N√A)) = −(4πR/N)(ρ + p_r).
In Morris–Thorne variables it becomes
4π∫ r e^{−Φ}(ρ + p_r)(1 − b/r)^{−1/2} dr = −Δ[e^{−Φ}√(1 − b/r)].

Integrating over any interval [l₁, l₂]:

- 4π∫(R/N)[−(ρ + p_r)] dl = (R′/N)(l₂) − (R′/N)(l₁);
- hence **B₋ := 4π∫(R/N) max[−(ρ + p_r), 0] dl ≥ Δ(R′/N)**, with equality iff
  ρ + p_r ≤ 0 on the interval.

**Per-end bound, with its exact hypotheses.** Suppose:

- R′ = 0 at l₁ (a throat or a uniform track);
- the end is asymptotically flat with R′ → 1 and N → N_∞;
- N > 0 throughout (no horizon).

Then **B₋ ≥ 1/N_∞**. With the standard normalization N_∞ = 1 this is **≥ 1 per
end**, and a static two-ended wormhole needs B₋ ≥ 1/N₊ + 1/N₋ (= 2
ultrastatically). A uniform continuation (R′ ≡ 0) needs no radial deficit.
Toward a closing cap with ρ + p_r ≥ 0, R′/N decreases, as the identity requires.

**Distributional extension.** For piecewise-C² profiles the integral is
distributional, and a thin shell contributes its surface null energy to B₋.

**Added hypotheses.** The inventory's "≥ 1 per end" silently assumes three
things:

- lapse normalized to 1 at the end: the measure scales as 1/N_∞ while ρ + p_r
  is normalization-free;
- N > 0;
- R′ → 1 at the end.

**Notation.** With class-S notation (A = γ_ll, unit lapse) the displayed
formula is false (counterexample at random jets). The correct unit-lapse form
is ∂_l(∂_lR/√A) = −4πR√A(ρ + p_l).

**Unification.** A static radial null ray of unit Killing energy has
T(k,k) = (ρ + p_r)/N², dR/dλ = R′/N and dλ = N dl. The identity is therefore
**I2 integrated along the ray**. This yields a time-dependent version valid in
any spherically symmetric spacetime: along every affinely parametrized radial
null geodesic, **4π∫R T(k,k) dλ = −Δ(dR/dλ)**. Any radial ray on which dR/dλ
increases by D therefore crosses an R-weighted null deficit of at least D. The
bound is covariant under k → ck, which rescales both sides by c.

**Method.**

- Jet identity in the general and report gauges.
- Ellis: 4π∫₀^∞ R[−(ρ+p_r)]dl = 1 exactly.
- mpmath quadratures for R² = l² + 1 with four lapse profiles: signed
  integral −1/N_∞ to 10⁻¹⁸. One profile with ρ + p_r > 0 regions gives
  B₋ = 4.497 ≥ 1 (two sign changes).
- Schwarzschild exterior: R′/N ≡ 1.
- Time-dependent geodesic check: RK4 along a radial null geodesic of a metric
  with α, β, A, B all (t,l)-dependent. 4π∫R T(k,k)dλ + dR/dλ stays constant to
  2×10⁻¹³ while dR/dλ changes by 1.85.

**Status.** The pointwise flare-out is standard (Morris–Thorne 1988;
Hochberg–Visser 1997). The exact integral identity, the ≥ 1/N_∞ per-end bound
and the time-dependent ray form are new in this form. The closest literature
is the ANEC and volume-integral quantifiers of Visser–Kar–Dadhich 2003 and
Kar–Dadhich–Visser 2004. VKD's radial ANEC is ∫(ρ + p_r)/N dl; the identity
here is its R-weighted version, which is an exact total derivative.

### I19. Clock identity — VERIFIED WITH CORRECTED HYPOTHESIS (nondegenerate maximum)

**Statement.** In a static region (l proper distance, lapse N; the reports'
"A"):

**(R²N′)′ = 4πR²N(ρ + p_r + 2p_t).**

- General radial gauge: A^{−1/2}∂_l(R²∂_lN/√A) = 4πR²N(ρ + p_r + 2p_t).
- It is the spherical form of the static Tolman–Whittaker/Komar relation
  D²N = 4πN(ρ + Σp_i), where 4π(ρ + Σp_i) = R_ab u^a u^b for static observers.
- At N′ = 0, 4πN(ρ + p_r + 2p_t) = N″. A nondegenerate interior lapse maximum
  (N″ < 0) therefore requires ρ + p_r + 2p_t < 0 there: a violation of the
  strong energy condition for static observers, independent of the null
  conditions.
- A potential-dominated source T = −Vg supplies ρ + p_r + 2p_t = −2V while
  saturating both null conditions (ρ + p_r = ρ + p_t = 0).

**Correction.** "A strict interior lapse maximum needs a negative value there"
holds at a nondegenerate maximum. At a degenerate strict maximum the source
can vanish at the point, and it is negative somewhere in every neighbourhood,
since R²N′ changes sign from + to −.

**Status.** Standard: Tolman 1930; Whittaker 1935; Komar 1959. The lit
inventories reference Komar through the one-space I10 comparison
(`lit_parts/lapse_only_nec.md`) and the related Hochberg–Visser 1997 result
ρ − τ ≤ 0 at lapse maxima on the throat. The anchors should be added.

### I20. Static conservation — VERIFIED

**Statement.** p_r′ + (N′/N)(ρ + p_r) + 2(R′/R)(p_r − p_t) = 0, the radial
component of ∇_μT^μν = 0 for a static diagonal T. It holds identically for
every static class-S Einstein tensor, in any radial gauge with ′ = d/ds.

**Status.** Standard: the anisotropic TOV equation (Bowers & Liang 1974, to be
added); Morris–Thorne 1988 give the same force balance in (b, Φ) form.

### I21. Ellis closed form — VERIFIED

**Statement.** For ds² = −dt² + dl² + (l² + a²)dΩ²:

- ρ = p_l = −a²/(8π(l²+a²)²), p_Ω = +a²/(8π(l²+a²)²), j = 0;
- the tensor is Type I with negative energy density and an |l|⁻⁴ tail.

Tail norm: the orthonormal Frobenius norm √(ρ² + p_l² + 2p_Ω²) = a²/(4πR⁴),
integrated over both ends beyond L with measure 4πR²dl, equals
2a arctan(a/L) ~ 2a²/L.

Constant angular jacket, B = (l² + a²)c²:

- ρR² → (1 − c²)/(8π) and p_lR² → −(1 − c²)/(8π);
- p_ΩR² → 0;
- this is a string-cloud (solid-angle-deficit) tail.

**Status.** Standard (Ellis 1973; Bronnikov 1973; the Ellis–Bronnikov
wormhole of `lit_parts/wormholes.md`). The jacket tail is the
global-monopole/string-cloud structure (Barriola–Vilenkin 1989; Letelier 1979).

### I22. Static geometries are Type I in the radial block — VERIFIED (and extended)

**Statement.** If α, A, B are t-independent and β = 0 on an open set, then:

- j_l = 0;
- T is diagonal in the static orthonormal frame, hence Type I;
- the two radial null energies are equal.

**Extension (verified).** Let α, β, A, B be t-independent (stationary, shift
allowed). Let ξ = ∂_t, and let ζ = (−g_tl, g_tt) be its quotient-orthogonal
partner. Then:

- G(ξ, ζ) = 0 identically;
- g(ζ,ζ) = g_tt det(g_ab).

So wherever g_tt ≠ 0 the normalized pair (ξ, ζ) is an orthonormal radial frame
that diagonalizes T, and Δ = (T(u,u) + T(s,s))² ≥ 0. That is Type I in static
regions and in homogeneous regions (g_tt > 0) alike.

**Consequences.**

- Radial Type IV requires the absence of any Killing field in the quotient
  that is non-null at the point.
- A static or stationary surrogate cannot detect Type IV.

**Status.** Standard: with back-reaction, Type I is forced in static
spacetimes (Martín-Moruno & Visser 2021, lit_foundations 1.6). The
stationary-with-shift extension is elementary in spherical symmetry.

### I23. Canonical condensates supply no null deficit — VERIFIED WITH ADDED HYPOTHESES

**Statement.** Take a static background, a minimally coupled charged scalar
φ = f(l)e^{−iωt} with gauge potential A_t = Φ(l), and potential V(|φ|²). Then

- (ρ, p_r, p_t) = (K+D+V+E, K+D−V−E, K−D−V+E), with j = 0;
- K = (ω + qΦ)²f²/N², D = (df/ds)², E = E_r²/(8π);
- the radial null stress is 2(K + D) ≥ 0 and the angular null stress is
  2(K + E) ≥ 0. Neither depends on V, whatever its sign.

For a minimally coupled real scalar of kinetic sign ε with arbitrary time
dependence:

- T(k,k) = ε(k·∂φ)² for both radial null k;
- sgn(ρ + p_l) = ε and p_l − p_Ω = ε(e_l·∂φ)²;
- Δ ≥ 0, so the block is never radial Type IV.

A sum of components with non-negative null energy has non-negative null
energy (so it cannot reduce the null requirement) and is never radial Type IV
(I3).

**Correction.** The inventory calls the scalar block "boost-diagonalizable".
That holds where ∂φ is non-null. Where ∂φ is null and non-zero,
T(k+,k+) = 0 ≠ T(k−,k−) and j ≠ 0, so Δ = 0 and the block is Type II.

**Added hypotheses.** Minimal coupling. Positive kinetic sign (ε = +1) for the
NEC statement. Curvature-coupled scalars (ξRφ²) lie outside the statement.

**Method.** Field-theory T from the Lagrangian (explicit engine; D_μ = ∂_μ − iqA_μ;
Maxwell stress in Gaussian units); jet scalar field of either kinetic sign;
null-gradient substitution.

**Status.** Standard: canonical scalars and Maxwell fields satisfy the NEC
(Kontou & Sanders 2020, lit_foundations 1.1; Martín-Moruno & Visser 2017,
lit_foundations 1.7).

### I24. The minimal Type I regulator — VERIFIED WITH ADDED HYPOTHESIS (h ≠ 0)

**Statement.** Set reg = max(0, 2|j| − |h|) and δρ = δp = ½sgn(h)·reg, with
δj = δp_Ω = 0. Then:

- |h_new| = 2|j| exactly, so Δ = 0;
- for j ≠ 0 the regulated block is a Jordan block, **Type II** (exactly
  luminal) and not Type I;
- a safety factor s gives |h_new| − 2|j| = (s − 1)(2|j| − |h|), so s > 1 is
  Type I;
- minimality: |h + δh| ≥ 2|j| forces |δh| ≥ 2|j| − |h| (triangle inequality),
  and δh = sgn(h)·reg attains it;
- the regulated tensor is a different T from the Einstein demand.

**Added hypothesis (corner case).** At h = 0 with j ≠ 0, sgn(0) = 0 makes the
prescription void and leaves Δ = −4j². A sign has to be chosen there; either
sign attains the minimum 2|j|.

**Status.** A design construct with elementary algebra.

### I25. Heat-mode speed and the Type I margin — algebra VERIFIED; physical reading MODEL-SPECIFIC

**Statement (verified).** D = (ρ + p_l)²(1 − v_q²), with v_q := 2j/|ρ + p_l|.

For a Type I block boosted by rapidity η from its rest frame, v_q = tanh(2η):
the rapidity of v_q is twice the rapidity of the rest frame relative to the
normal observer. It approaches 1 exactly as the block approaches the Type II
boundary, since the rest frame becomes null.

**Model-specific part.** The reading "a medium realizing a near-Type-II block
has a near-luminal heat characteristic" identifies v_q with a characteristic
speed of the project's reduced heat-current constitutive model
(`STAGE2_BETA075_SOURCE_FAMILY_EQUATION_PACKAGE.md`). That is a property of the
model, not of the identity. The measured margin coincidence (7.881e-5 vs
7.983e-5) is design-specific.

**Status.** The algebra is elementary; v_q = tanh 2η is new in this form.

### I26. Boosted infrastructure preserves the discriminant — VERIFIED

**Statement.** Boosting a rest-frame radial block (E_b, P_b, 0) by ψ:

- adds D = h_b sinh²ψ to both E and P, with h_b = E_b + P_b;
- produces j_b = (h_b/2) sinh 2ψ, i.e. ψ = ½ asinh(2j_b/h_b);
- leaves Δ = h_b² unchanged.

Speed bound: the registered response j_b = Jc²h_b²/(J² + c²h_b²) satisfies
the bound `|2j_b/h_b| ≤ c` for all J and h_b, since
`J² + c²h_b² − 2|J|c|h_b| = (|J| − c|h_b|)² ≥ 0`. With
c = 2v_max/(1 − v_max²) = sinh(2 artanh v_max), this gives `|v| ≤ v_max`.

**Status.** Boost algebra is standard; the saturating parametrization is a
design choice.

### I27. Areal-gauge mass relations — VERIFIED

**Statement.** In ds² = −α²dt² + dr²/f + r²dΩ² with f = 1 − 2m/r (zero shift,
areal radial coordinate), with time dependence allowed:

- E = m_r/(4πr²);
- ∂_r log α = (m + 4πr³P_r)/(r(r − 2m));
- ∂_t m = −4πr²α√f J, where E, P_r, J are measured by the areal observers and
  J is the outward energy flux;
- 8πP_t = f(ν_rr + ν_r² + ν_r/r) + ½f_r(ν_r + 1/r) + (f_tt − f_tν_t − 3f_t²/(2f))/(2α²f),
  with ν = log α;
- second time derivatives enter P_t alone.

The static form m_b = (r/2)[1 − (∂_lr)²/γ_ll] is the Misner–Sharp mass. In
general class S, m = (R/2)[1 + (nR)² − (e_lR)²], so m_b needs n(R) = 0.

The general gradient identity ∂_a m = 4πR²(T^b_a∂_bR − T^c_c∂_aR) (quotient
trace) holds for all class-S metrics.

**Status.** Standard (Misner & Sharp 1964; the TOV structure; Hayward 1996).
These anchors should be added to the lit inventories.

### I28. Onset obstruction — DESIGN-SPECIFIC (specific to the registered families); general lemma VERIFIED

**General lemma (verified).** In the areal gauge, second time derivatives of
the metric enter the angular equation alone, through f_tt/(2α²f). Suppose at a
boundary log f = log f_i + a uⁿ + …, t = τ₀u + O(u²), and the lapse changes at
O(u^{n−1}). Then:

- the time part of 8πP_{t,G} is n(n−1)a u^{n−2}/(2α_i²τ₀²) + O(u^{n−1});
- the current is J = j_* u^{n−1} + …, with j_* = n√f_i a/(8πrα_iτ₀).

Checked for n = 3, 4, 9. The angular demand, O(u^{n−2}), therefore leads the
current, O(u^{n−1}), by one order and any response quadratic in J,
O(u^{2n−2}), by n orders. The same
ordering holds for every power-law onset and for flat C^∞ onsets such as
e^{−1/u}, since f_tt/f_t² diverges at onset in both cases.

**Registered families (verified expansions).**

- Moving infrastructure: j_b = J − J³/(c²h²) + … and D = J²/h + O(J⁴).
- Stationary infrastructure: M = −|J|.
- The newly supplied material, and hence its angular stress, starts at
  u^{2n−2}, so exact angular closure fails at onset.

**Verdict.** The obstruction holds for its registered families and boundary
contract, as the report itself scopes it (`LE_RESET_INVERSE_SEARCH.md`:419–421).
The general content is a necessary condition on any source: at onset, its
angular (equivalently, radial-force) stress must respond linearly to the
geometric acceleration f_tt. Source families with stored stress or an
acceleration-linear response can meet it; the report's Comer–Andersson
follow-up supplies such a term. It does not exclude spherical resets in
general.

**Status.** Design-specific. The lemma is elementary.

---

## 6. One-space I24 (knobs_one_space.md §3.1) — cross-check: CONSISTENT (6/6)

One-space I24 restates four throat-era identities, and each re-verifies
directly:

| One-space I24 clause | Same as | Result |
|---|---|---|
| 8πT(k,k) = −(2/R)k^ak^b∇_a∇_bR | I2 | holds |
| Δ = (ρ+p_ℓ)² − 4j_ℓ² = T(k₊,k₊)T(k₋,k₋) | I3 | holds |
| (R′/A)′ = −(4πR/A)(ρ+p_ℓ), ≥ 1 per end | I18 | holds with A = lapse and l = proper distance |
| string boost invariance | I4 | holds |

It carries the same hypotheses as I18: lapse normalized at the end, no horizon,
R′ → 1. It also carries the notation hazard: read with class-S notation
(A = γ_ll), the formula is false, and the correct unit-lapse form is
∂_l(∂_lR/√A) = −4πR√A(ρ + p_ℓ). The book should write the lapse as N (or α)
in every static formula.

---

## 7. Summary table

Suggested book tags: T theorem, D derived and symbolically checked,
L literature, H heuristic, M measured.

| Item | Identity | Result | Standard or new | Suggested tag |
|---|---|---|---|---|
| I1 | Warped-product Einstein tensor | VERIFIED | Standard (O'Neill; Gerlach–Sengupta; Hayward; anchors to add) | L + D |
| I2 | Radial null energy = null Hessian of R; affine and Raychaudhuri forms | VERIFIED | Standard (focusing equation) | L + D |
| I3 | Δ = T(k₊,k₊)T(k₋,k₋); boost invariance; rest frame; Type II at Δ = 0 | VERIFIED | Standard algebra (MM–V 2021); product form new in this form | D |
| I4 | Constant R ⇒ exact boost-invariant string cloud; p_Ω = −K/8π | VERIFIED | Standard (product spacetimes; Letelier) | D |
| I5 | Radial null speeds; ergo-like criterion; trapped when ∂_tR = 0 | VERIFIED | Standard | D |
| I6 | Packet norm and clock | VERIFIED | Standard | D |
| **I7** | Shift re-match algebra; "price only via ∂β" | Algebra VERIFIED; remark **FALSE**, CORRECTED (β enters through n = α⁻¹(∂_t − β∂_l)) | Design construct; corrected structure standard 3+1 | D |
| I8 | α² in coordinate-normalized null energy | VERIFIED | Standard | D |
| I9 | Uniform slowdown: X_κ = X₀ + κ²(X₁ − X₀), j_κ = κj₁, Δ_κ at h₀ = 0 | VERIFIED (any 3+1 metric) | New in this form | T/D |
| I10 | Null-expansion "proxy" | VERIFIED: the proxy is the exact expansion | Standard | D |
| **I11** | Radial bundle focusing independent of B | VERIFIED WITH ADDED SCOPE (in-quotient separation; areal focusing depends on B) | Elementary | D |
| I12 | String-cloud flux ∂(μR²) = 0; 8πμR² = 1 − (∇R)² − R□R | VERIFIED | Standard (Letelier) | D |
| **I13** | Join regularity d^p ⇒ d^{p−2} | VERIFIED WITH ADDED HYPOTHESES; general rule and exceptions (∂_t²α, ∂_t∂_lα, ∂_t²β; static ∂_l²A) | Ingredients standard; rule new in this form | T/D |
| I14 | Lapse-only dynamics: j = 0, ρ = ³R/16π | VERIFIED (open regions) | Standard (momentum constraint) | L + D |
| I15 | Divergence does not fix type | VERIFIED | Standard | D |
| **I16** | 8π(ρ,p_r,p_t) = W(1,−1,0) + Z(−2,0,1) + Y(0,2,1) + X(0,0,1) | VERIFIED; role of W CORRECTED (radially null-neutral only) | Content standard; packaging new | D |
| **I17** | Tension −1/(8πR²) vs opening −R″/(4πR) | VERIFIED; "strict min ⇒ R″ > 0" **FALSE**, CORRECTED | Standard (MT 1988; H–V 1997) | L + D |
| **I18** | (R′/N)′ = −(4πR/N)(ρ + p_r); B₋ ≥ Δ(R′/N); ≥ 1 per end | VERIFIED WITH ADDED HYPOTHESES (N_∞ = 1, N > 0, R′ → 1; A = lapse); time-dependent ray form added | Pointwise standard; integral identity and bound new in this form | T/D |
| **I19** | (R²N′)′ = 4πR²N(ρ + p_r + 2p_t) | VERIFIED WITH CORRECTED HYPOTHESIS (nondegenerate maximum) | Standard (Tolman/Whittaker/Komar) | L + D |
| I20 | Static anisotropic TOV | VERIFIED | Standard (Bowers–Liang; MT) | L + D |
| I21 | Ellis closed form; tail 2a arctan(a/L); jacket tail | VERIFIED | Standard (Ellis 1973; Bronnikov 1973) | L + D |
| I22 | Static ⇒ Type I (extended to all stationary regions) | VERIFIED | Standard (MM–V 2021) | L + D |
| **I23** | Canonical condensates: null stresses 2(K+D), 2(K+E) ≥ 0; scalar never Type IV | VERIFIED WITH ADDED HYPOTHESES (minimal coupling, ε = +1); Type II where ∂φ null | Standard (Kontou–Sanders) | L + D |
| **I24** | Minimal Type I regulator | VERIFIED WITH ADDED HYPOTHESIS (h ≠ 0); factor 1 gives Type II | Design construct | D |
| **I25** | D = h²(1 − v_q²); heat-mode speed | Algebra VERIFIED (v_q = tanh 2η); physical reading MODEL-SPECIFIC | Algebra new in this form | D + H |
| I26 | Boost preserves Δ; speed bound v ≤ v_max in magnitude | VERIFIED | Standard algebra; design parametrization | D |
| I27 | Areal-gauge mass relations | VERIFIED (m_b needs n(R) = 0) | Standard (Misner–Sharp; TOV; Hayward) | L + D |
| **I28** | Onset obstruction | DESIGN-SPECIFIC (registered families); general lemma VERIFIED | Design-specific | M / D (lemma) |
| X24 | One-space I24 | CONSISTENT; notation hazard A = lapse | — | — |
