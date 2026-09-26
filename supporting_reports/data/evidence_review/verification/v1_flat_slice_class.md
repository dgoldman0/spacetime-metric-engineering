# Verification v1: the flat-slice lapse–shift class (C0)

**Files.** Script `v1_flat_slice_class.py` (sympy, written from scratch); run log
`v1_flat_slice_class.log`. Run with

    nice -n 10 env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 v1_flat_slice_class.py

The script is deterministic (fixed seeds) and runs in about 70 s on one core. It performs 134 checks,
and every check comes out as recorded below (exit status 0).

**Independence.** No code from the repository or from `verify_identities.py` / `verify_compact.py` was read or
used. The repository reports were read only for the exact wording of each statement.

**Conventions** (book, `05_STRUCTURE.md`). Signature (−,+,+,+); G_ab = 8πT_ab; MTW Riemann;
K_ij = −(1/2α)(∂_tγ_ij − D_iβ_j − D_jβ_i), so K = −∇_μn^μ (checked, Item 2); ρ = T(n,n),
j_i = −T(n,e_i), S_ij = T(e_i,e_j).

**Class C0** (C0A when A ≠ 1): ds² = −α²dt² + A²(dz + β dt)² + dr² + r²dφ², with α > 0, A > 0 and β
functions of (t, z, r). Frame: n = (∂_t − β∂_z)/α, e_z = A⁻¹∂_z, e_r = ∂_r, e_φ = r⁻¹∂_φ. "8πT_ab" always
means orthonormal lower components in this frame.

**Notation.** a = ln α, b = ln A, s = β_r/α (proper radial shear), 𝒦 = β_z/α,
n(f) = α⁻¹(∂_t − β∂_z)f, Q = n(𝒦) − 𝒦², Δ⊥f = f_rr + f_r/r. The *service curvature* K at radius r is the
Gaussian curvature of the 2D metric −α²dt² + A²(dz + βdt)² at fixed r, normalized by R₍₂₎ = 2K.

**Method.**
- *Engine.* The metric components are differentiated twice. Every derivative of an undefined function is
  then replaced by an independent jet symbol. Christoffel symbols, their derivatives, and the Ricci and
  Einstein tensors are assembled algebraically.
- *Why this is general.* G at a point depends only on the 2-jet of the metric there. An identity between
  rational functions of arbitrary jets at a generic point therefore holds for all C² fields.
- *Two checks per identity.* (i) Symbolic: the numerator of the difference, over a common denominator,
  expands to zero. (ii) Exact evaluation at random rational jets. A guard rejects any floating-point number
  inside a symbolic check.
- *Negative controls.* Deliberately wrong formulas are rejected.
- *Explicit examples.* Evaluated with mpmath at 40 digits. The Hawking–Ellis type comes from the
  eigen-decomposition of T^a_b: a complex pair means Type IV; a real spectrum with a timelike eigenvector
  means Type I.

---

## Step 0. Engine validation

| Case | Check | Outcome |
|---|---|---|
| Schwarzschild in Painlevé–Gullstrand form: flat slices, unit lapse, β = √(2M/r) | G_ab ≡ 0. Control: R^t_{rtr} = 2M/r³ ≠ 0 | exact |
| Flat FRW, a(t) | G_tt = 3H², G_xx/a² = −(2ä/a + H²). Dust a ∝ t^{2/3}: ρ = 3H²/8π, p = 0. Radiation: p = ρ/3. de Sitter: p = −ρ | exact |
| Alcubierre flat-slice metric, β^x = B(t,x,y,z) | G(n,n) = −(B_y² + B_z²)/4 for every B | exact |
| Alcubierre (1994) eq. (19), tanh profile (v_s = 3/2, σ = 8, R = 1), 4 random events including t ≠ 0 | ρ from the engine vs −(1/8π)(v_s²ρ_⊥²/4r_s²)(f′)²: largest relative difference 8×10⁻³⁹ | 40 digits |

---

## Item 1. Complete orthonormal tensor of C0 with A = 1 (inventory §3.2)

**Statement.** Take ds² = −α²dt² + (dz + βdt)² + dr² + r²dφ², with α(t,z,r) > 0, β(t,z,r) of class C² and
r > 0. Then:

| Component | 8π × component |
|---|---|
| T_nn = ρ | −s²/4 |
| T_nz | −(1/2r)∂_r(r s) |
| T_nr | (1/2α²)∂_z(α²s) − 𝒦∂_r a  (= ∂_r𝒦 − ½∂_z s) |
| T_zz | Δ⊥α/α − 3s²/4 |
| T_rr | (α_zz + α_r/r)/α + s²/4 + Q |
| T_φφ | (α_rr + α_zz)/α − s²/4 + Q |
| T_zr | −α_rz/α − ½n(s) + s𝒦 |
| T_nφ, T_zφ, T_rφ | 0 |

The null sums follow:
- 8π(ρ + p_z) = Δ⊥α/α − s²;
- 8π(ρ + p_r) = (α_zz + α_r/r)/α + Q;
- 8π(ρ + p_φ) = (α_rr + α_zz)/α − s²/2 + Q.

**Method.** Symbolic check of all ten components, the three null sums and the compact form of T_nr, plus
exact rational probes. Two negative controls (a flipped sign in T_nz; T_zr without s𝒦) are rejected.

**Result: VERIFIED.**

**Derivation.**
- *Extrinsic curvature.* From the definition (Item 2 with A = 1): K_ẑẑ = 𝒦 and K_ẑr̂ = s/2; all other
  components vanish.
- *Energy.* The Hamiltonian constraint on flat slices gives 16πρ = K² − K_ijK^ij = −s²/2.
- *Fluxes.* The momentum constraint 8πj_i = D_jK^j_i − D_iK, with T_nî = −j_i, gives
  8πT_nz = −(1/2r)∂_r(rs) and 8πT_nr = ∂_r𝒦 − ½∂_z s.
- *Stresses.* The evolution equation with ³R_ij = 0 reads
  8π[S_ij − ½γ_ij(S − ρ)] = −α⁻¹(∂_t − L_β)K_ij − α⁻¹D_iD_jα + KK_ij − 2K_ikK^k_j.
  The time derivatives enter only through (∂_t − L_β)K_ij, which produces n(𝒦) and n(s).

A direct computation of G_ab reproduces the table.

---

## Item 2. I1, the energy density (A ≡ 1 and A ≠ 1)

**Statement (A ≡ 1).** ρ = −(β_r/α)²/32π for every α(t,z,r) > 0 and β(t,z,r). Consequences:
- ρ ≤ 0;
- β_z drops out;
- the lapse enters only as α⁻².

**Statement (A ≠ 1, class C0A with A(t,z,r) > 0).** Exactly,

  ρ = −(Aβ_r/α)²/32π − Δ⊥A/(8πA).

The report's form ρ = −(Aβ_r/α)²/32π therefore holds exactly whenever Δ⊥A = 0. This covers every stretch
A = A(t,z) that depends on time and on position along the track. A_t and A_z never enter ρ, and the factor
A is the proper-shear factor. The auxiliary results are:
- K_ẑẑ = (β_z + βA_z/A − A_t/A)/α = 𝒦 − n(b);
- K_ẑr̂ = Aβ_r/(2α), and all other K_îĵ = 0;
- K = −∇_μn^μ;
- ³R[A²dz² + dr² + r²dφ²] = −2Δ⊥A/A.

**Method.** K_ij is computed from its definition, with 3D covariant derivatives. ³R comes from the engine
in 3D and ρ from G(n,n). The Hamiltonian constraint 16πρ = ³R + K² − K_ijK^ij is checked against the 4D
engine. All checks are symbolic.

**Result.**
- A ≡ 1: **VERIFIED.**
- A ≠ 1: **VERIFIED WITH CORRECTED FORMULA** (above). The inventory note in §3.3 item 2 ("the formula does
  not hold for non-constant A") is too strong. The formula holds for all A(t,z) and fails only through the
  transverse Laplacian of A.

**Derivation.** With k = K_ẑẑ and s_A = Aβ_r/α, K² − K_ijK^ij = k² − (k² + 2(s_A/2)²) = −s_A²/2. The trace
k cancels, which is why A_t and A_z drop out. The Hamiltonian constraint then gives
16πρ = −2Δ⊥A/A − s_A²/2.

---

## Item 3. I2, the pure-lapse identity, and I18, the directional form

**Statement (I2, precise hypotheses).** Consider a spacetime region where:
- the spatial metric is flat and static;
- for an open interval of time, the shift is a Killing field of that metric. In particular this includes a
  spatially uniform shift β^i = b^i(t), and a rigid rotation b(t) + Ω(t)×x is allowed;
- α(t, x) > 0 is arbitrary, time dependence included.

Then:
- K_ij = 0, ρ = 0 and j = 0;
- 8πT_ij = (δ_ij Δα − ∂_i∂_jα)/α, with no time derivatives;
- the tensor is Hawking–Ellis Type I for every profile and history.

The time interval matters. At an instant where the shift's spatial gradients vanish but their time
derivatives do not, ρ = j = 0 and Type I still hold. The stress, however, gains terms: 8πT_rr and 8πT_φφ
gain β_zt/α², and 8πT_zr gains −β_rt/(2α²).

On a curved static slice with zero shift (Item 13a), ρ = ³R/16π, j = 0 and
8πS_ij = ³G_ij + (γ_ijD²α − D_iD_jα)/α.

**Statement (I18).** In a pure-lapse region, for every unit spatial vector e,

  8πT(n+e, n+e) = (Δα − ∂_e²α)/α = Δ_{e⊥}α/α,

where Δ_{e⊥} is the Laplacian of α within the plane orthogonal to e. For axisymmetric α(r, z):

| Light moving | 8πT(n+e, n+e) |
|---|---|
| radially | (α_zz + α_r/r)/α |
| axially | (α_rr + α_r/r)/α |
| azimuthally | (α_rr + α_zz)/α |

The shear stress is 8πT_zr = −α_rz/α. Two further statements hold:
- *On a regular axis*, for axial light: T(k,k) = α_rr/(4πα).
- *Radial ray through a static fall with α = α(r)* (so α_zz = 0 along the ray): k = (E/α)(n + e_r) is
  affinely parametrized, and ∫T(k,k)dλ = (E/8π)∫α′/(rα²)dr. It is negative wherever α falls outward.

  The inventory's "every lapse hill violates radial NEC on its fall" holds pointwise where α_r < 0 and
  α_zz ≤ 0. Item 4 gives the global statement.

**Method.** The general Cartesian case uses α(t,x,y,z) with b(t), all six stress components. The C0 case
uses β = β(t). The Killing-shift extension is evaluated at a generic point: b + Ω×x equals
(b + Ω×p) + Ω×(x − p), so the origin is generic. Further checks: the instant-only case from the Item 1
table, a symbolic limit on the axis, and the radial null geodesic equation. All symbolic.

**Result: VERIFIED WITH ADDED HYPOTHESES.**
- The shift must be uniform, or Killing, on a time interval.
- The radial-ray integral needs α = α(r) along the ray.

The identity extends to Killing shifts, rigid rotation included.

**Derivation.**
1. For a Killing shift of a flat static slice, K_ij = (1/2α)(∂_iβ_j + ∂_jβ_i) = 0. The constraints give
   ρ = ³R/16π = 0 and j = 0.
2. Because K ≡ 0 on a time interval, ∂_tK_ij = 0. The evolution equation reduces to
   0 = −D_iD_jα + α³R_ij − 8πα[S_ij − ½γ_ij(S − ρ)].
3. Taking the trace gives S = D²α/(4πα), hence the stress formula.
4. With j = 0, n is an eigenvector of T^a_b and the spatial block is symmetric, so the tensor is Type I.
5. For I18: T(n+e,n+e) = ρ + 2j·e + S_ee = S_ee = (Δα − e·∇∇α·e)/(8πα).

---

## Item 4. The lapse-only NEC lemma (02_SYNTHESIS §2.1)

**Statement as given.** "On flat slices with α → 1, every non-constant lapse violates the NEC somewhere
(Komar-mass argument)."

**Corrected statement (Lemma).** Take a slice that is flat and static, with the shift a Killing field (e.g.
uniform) on the *whole* slice for an open time interval (the hypotheses of Item 3), and α > 0 of class C².

- (a) For every unit e: 8πT(n+e,n+e) = Δ_{e⊥}α/α.
- (b) **Plane form.** Suppose α is bounded above on an affine plane P, and the null energy of light
  crossing P along its normal is ≥ 0 at every point of P. Then α is constant on P.
- (c) **Global form.** Suppose α → 1 at spatial infinity and α is non-constant on the slice. Then for every
  direction e some point of the slice has T(n+e, n+e) < 0. More precisely, through every point where
  α ≠ 1, every plane carries such a violation for light crossing it normally. No fall-off rate is needed.
  - If α is only bounded above, the violation still occurs for every direction e along which α is not a
    function of x·e alone.
  - For α = f(x·e), which is bounded and non-constant, f″ < 0 somewhere, so every other direction is
    violated. Light along e itself sees zero, as for α = 2 + tanh x.
- (d) **Localized form.** Suppose the hypotheses hold only outside a closed set C (for example, the support
  of a non-uniform shift). Consider a plane disjoint from the closed convex hull of C, on which α is
  bounded above and non-constant. Some point of that plane carries a normal-light NEC violation. So with
  α → 1, any lapse contrast outside conv C is paid for by NEC violation outside conv C.
- (e) **Komar form.** For every orthonormal triad, α Σ_i 8πT(n+e_i, n+e_i) = 2Δα. Hence
  ∫αΣ_iT(n+e_i,n+e_i) d³x = (1/4π)∮∇α·dS = M_K, the Komar mass of the slice. If M_K = 0, the NEC forces
  Δα ≡ 0, so α is harmonic and bounded, hence constant. M_K = 0 holds for an exactly flat exterior, or for
  α − 1 = o(1/R) with ∂α = o(1/R²).

**Fall-off α − 1 ≈ −M/R.** Here M_K = M, and the Komar argument stops short. The lemma still holds:
- at large R, 8πT(n+e,n+e) = −M/(R³α) for tangential e and +2M/(R³α) for radial e, so one of the two
  families violates the NEC for either sign of M;
- example, the Plummer lapse α = 1 − M/√(R² + a²):
  - Δα = 3Ma²/(R²+a²)^{5/2} > 0 everywhere, so the direction-summed null energy is positive everywhere;
  - M_K = M (quadrature: 0.3 for M = 0.3);
  - yet 8παT = M(2a² − R²)/(R² + a²)^{5/2} < 0 for tangential light at R > √2·a.

**Counterexamples when the hypotheses fail.**
- *α unbounded.*
  - Rindler, α = 1 + gx: T ≡ 0.
  - α = 1 + |x|²: 8πT_ij = 4δ_ij/α, so every null energy is strictly positive.
- *Shift not Killing on the whole slice.*
  - In C0, α = cosh u(z) and β = sinh u(z), i.e. α = √(1 + β²), for example u = u₀ sech z. Every Riemann
    component vanishes: this is Minkowski space in a flat, non-hyperplane slicing. α is non-constant and
    tends to 1, and T ≡ 0.
  - Strict example: the interior Schwarzschild star (M/R = 1/5) in Painlevé–Gullstrand slicing, with
    α = e^Φ/√(1 − 2m/r) and β = α√(2m/r). The slices are flat and the shift is non-uniform. α rises from
    0.662 at the centre to 1 at the surface and equals 1 outside. T is the perfect fluid (ρ = 3M/4πR³ with
    TOV pressure), checked at r = 0.3, 0.6, 0.9 to 40 digits, with ρ + p > 0: the NEC holds strictly.

**Method.** Symbolic identities and examples; mpmath for the star; the classical Liouville theorems.

**Result: VERIFIED WITH CORRECTED HYPOTHESES.**
- The shift must be Killing (uniform) on the entire slice, as the counterexamples show.
- α must be bounded above, as the counterexamples show.
- The fall-off rate of α − 1 is irrelevant.
- The Komar argument proves the lemma only when M_K = 0. The plane argument proves it for every bounded
  lapse and yields the directional and localized forms (c) and (d).

**Derivation (book proof).**
- *(b).* By (a), with e normal to P, non-negativity on P means Δ_Pα ≥ 0, so α|_P is subharmonic on P ≅ ℝ².
  Liouville's theorem for subharmonic functions on ℝ² finishes the proof.
- *Liouville on ℝ².* Let u ≤ M be subharmonic and let m = max over |x| = r₀ of u. For ε > 0, the function
  u − m − ε ln(|x|/r₀) is subharmonic on the annulus r₀ < |x| < R. It is ≤ 0 on the inner circle, and ≤ 0 on
  the outer circle once R is large. The maximum principle gives u ≤ m + ε ln(|x|/r₀) for |x| ≥ r₀; letting
  ε → 0 gives u ≤ m there. With the maximum principle on the disc, u attains its supremum m at an interior
  point, so u is constant.
- *(c).* If T(n+e,n+e) ≥ 0 everywhere for a fixed e, then by (b) α is constant on every plane ⊥ e. It
  therefore equals its limit 1, so α ≡ 1.
- *(d).* A point outside a closed convex set lies on a plane disjoint from it (strict separation).
  Apply (b) on that plane.
- *(e).* Sum (a) over a triad. The divergence theorem gives M_K. When M_K = 0, bounded harmonic functions on
  ℝ³ are constant.

---

## Item 5. I3, uniform-field flatness; I26, occupant aging; I20, light speeds and static observers

**I3 statement.** Where α = α(t) and β = β(t) on a region of C0 (A = 1):
- the metric is Minkowski, via T = ∫α dt and x = z + ∫β dt;
- the Eulerian observers are geodesic. In general C0A the Eulerian acceleration is a(e_z) = A⁻¹∂_z ln α,
  a(e_r) = ∂_r ln α, a(e_φ) = 0, and it vanishes here;
- a packet carried at β = −v rests on the Eulerian observers (dz/dt = −β = v) and ages at dτ/dt = α.

Remark on the stretched class: in C0A with uniform α(t), β(t), A(t), the geometry is the product of the flat
plane with a (t,z) plane of curvature K = ∂_t(A_t/α)/(αA). It is flat if and only if A_t/α is constant.

**I26 statement.** Consider a compartment with uniform α_c and β = −v, and an exterior with α = 1 and β = 0.
Along the lane dτ/dt = α_c, so dτ/dz = α_c/v. Light crosses unit distance in unit exterior time, and on flat
slices z-distance is proper distance. The passenger therefore ages α_c/v of light's crossing time per unit
distance.

**I20 statement.** For motion along z at fixed (r, φ) in C0A:
- the coordinate speed is dz/dt = −β ± α/A, which is α/A in the standing geometry β = 0;
- rays of one family obey a first-order ODE with a Lipschitz right side, so distinct rays never cross;
- static observers (fixed z, r, φ) exist iff g_tt = −α² + A²β² < 0, i.e. α > A|β| (α > |β| in C0).

**Method.** All Riemann components (symbolic); the pull-back identity; the acceleration from the Christoffel
symbols; direct solution of the null condition.

**Result: VERIFIED** (I3, I26, I20).

**Derivation.** dT = α dt and dx = dz + β dt turn −α²dt² + (dz + βdt)² into −dT² + dx². The Eulerian
acceleration is D ln α. The null condition g_tt + 2g_tz ż + g_zz ż² = 0 has the roots −β ± α/A.

---

## Item 6. I4, the product (service-region) identity, and I4c, the sign of K

**I4 statement.** Let M = L² × Σ², where L² carries any Lorentzian 2-metric h of Gaussian curvature K
(R₍₂₎ = 2K) and Σ² = dr² + C(r)²dφ² has K_Σ = −C″/C. Then:
- in any orthonormal frame (n, e_z) of h, 8πT = diag(K_Σ, −K_Σ, −K, −K) in (n, z, r, φ);
- for unit e, 8πT(n+e,n+e) = (K_Σ − K)(1 − e_z²);
- the along-track null energies vanish, and the minimum over the Eulerian null sphere is
  min(0, (K_Σ − K)/8π);
- the tensor is Type I.

For a round sphere of radius R₀, ρ = −p_ℓ = 1/(8πR₀²) and p_Ω = −K/8π.

**I4c statement.** For A = 1 and r-independent fields, K = −α_zz/α − n(𝒦) + 𝒦². The sign convention checks:
de Sitter₂, with α = cos z, has K = +1. Then p_r = p_φ = [α_zz/α + n(𝒦) − 𝒦²]/8π, so the chain
"convex lapse ⇒ K < 0 ⇒ p_r > 0" requires α_zz/α > 𝒦² − n(𝒦). The convexity must exceed the shift's
contribution.

**Method.** Symbolic checks of all ten components, for a general 2D metric −α²dt² + A²(dz + βdt)² (α, β, A
functions of (t,z)) and general C(r). The 2D curvature comes from the engine in 2D.

**Result.**
- I4: **VERIFIED** (for any product).
- I4c: the formula is **VERIFIED**; the sign reading holds **WITH THE ADDED HYPOTHESIS**
  α_zz/α > 𝒦² − n(𝒦).

**Derivation.** On a product, Ric = K h ⊕ K_Σ σ and R = 2K + 2K_Σ, so G = −K_Σ h ⊕ −K σ.

---

## Item 7. I5 and I5c, the flux forms; I6, the shear identity

**I5c statement (exact, A = 1).**
- 8πT_nz = −(1/2r)∂_r(rβ_r/α);
- 8πT_nr = (1/2α²)∂_z(αβ_r) − (β_z/α)∂_r ln α = ∂_r𝒦 − ½∂_z s.

The fluxes are linear in β and carry a factor 1/α (times scale-free ∂ ln α); ρ is quadratic in β and carries
1/α².

With stretch, both fluxes are governed by the proper shear s_A = Aβ_r/α, which answers inventory §3.3 item 1:
- 8πT_nz = −(1/(2rA²))∂_r(rA²s_A);
- 8πT_nr = A⁻¹∂_r(A K_ẑẑ) − (2A)⁻¹∂_z s_A.

**I5 statement (report form, "≈").** Where β_r = 0 on a neighbourhood, two relations are exact:
- 8πT_nr = −β_z a_r/α;
- 8π(ρ + p_r) = a_r/r − K, with K the service curvature at that radius.

The report's approximations are these exact relations with K dropped.

**I6 statement (α = A = 1, any β(t,z,r)).**
- 8πT(n ± e_z, n ± e_z) = −(β_r² ± Δ⊥β), so the two along-track null energies have opposite signs iff
  |Δ⊥β| > β_r².
- The couplings to e_r are 8πT_nr = β_rz/2 and 8πT_zr = −(β_rt − ββ_rz)/2 + β_rβ_z.
- **Type IV holds** where the (n, z) plane is invariant. This means β_rz = 0 and β_rt = 2β_rβ_z; every static
  z-independent layer β(r) qualifies. By continuity it also holds where these couplings are small compared
  with the (n, z) splitting.
- **In general the Type IV clause is false.** Counterexample, static with α = 1:
  β = 2.1 + 4(r−1)z − (r−1)² at (z, r) = (0, 1).
  - Here Δ⊥β = −2 and β_r = 0, so (8π)²T(k₊,k₊)T(k₋,k₋) = −4 < 0.
  - Yet the eigenvalues of 8πT^a_b are {−4.09, 1.76, 2.33, 0}: Type I.
  - Replacing 2.1 by 0.5 gives Type IV.
  - Why: for β = V + 2B(r−1)z − (r−1)² at that point, the (n,z,r) cubic is λ³ + (1 + B² − V²B²)λ + 2VB² in
    units of 1/8π. It has three real roots only if V²B² > 1 + B². Type I in this family therefore requires
    |β| > α√(1 + B⁻²), a local shift faster than the local light speed.

**Block lemma** (used in Items 7–9). On an invariant timelike plane spanned by n and e, the 2×2 block of
T^a_b has discriminant (T_nn + T_ee)² − 4T_ne² = T(n+e,n+e)·T(n−e,n−e). It is Type IV iff the two null
energies have opposite signs.

**Method.** Symbolic checks, plus the full 4×4 eigen-decomposition at 40 digits for the counterexample.

**Result.**
- I5c: **VERIFIED**.
- I5: **VERIFIED WITH ADDED HYPOTHESES** (β_r ≡ 0 locally; the −K term restored).
- I6 null-energy identity: **VERIFIED**.
- I6 Type IV clause: **FALSE** in general. It is true where the (n,z) plane is invariant, as stated above.
- The proper-shear statement (§3.3 item 1): **VERIFIED**.

**Derivation.**
- *I5c.* Momentum constraint (Item 1).
- *I6.* T_nn ± 2T_nz + T_zz from the Item 1 table with α = 1.
- *Type IV.* The block lemma. With T_nr, T_zr ≠ 0, the type is decided by the (n, z, r) cubic (Item 9).

---

## Item 8. I7, the doubly warped Hessian identity

**Statement.** Take ds² = −α²dt² + A²dz² + dr² + C²dφ² with α, A and C functions of (t, r) only
(z-independent, β = 0). Let ∇∇ be the Hessian of the base metric −α²dt² + dr², and k± = n ± e_r. Then:
- 8πT(k±, k±) = −∇∇A(k±,k±)/A − ∇∇C(k±,k±)/C;
- for C = r, the second term equals α_r/(rα);
- the z and φ directions decouple: T_nz = T_zr = T_nφ = T_rφ = T_zφ = 0. The (n, r) block is therefore
  invariant, and it is Type IV iff T(k₊,k₊)T(k₋,k₋) < 0;
- T(k₊,k₊) − T(k₋,k₋) = −4[∇∇A(n,e_r)/A + ∇∇C(n,e_r)/C], the mixed Hessian;
- for static fields the two null energies coincide.

**Method.** Symbolic.

**Result: VERIFIED.** It holds also when C depends on t.

**Derivation.** For a doubly warped product B ×_A S¹ ×_C S¹ with 1D fibres,
Ric(X,Y) = Ric_B(X,Y) − ∇∇A(X,Y)/A − ∇∇C(X,Y)/C for X, Y tangent to B. On a 2D base, Ric_B = K_B g_B,
which vanishes on null k, and G(k,k) = Ric(k,k).

---

## Item 9. I8, the lapse envelope α > 2r|β_z|

**Statement as given.** "Type I requires α > 2r|β_z| wherever the lapse varies radially under a shift that
varies along the track."

**Exact (n, r) discriminant (C0, A = 1).** 8π(ρ + p_r) = a_r/r − K holds exactly, with K = −α_zz/α − Q the
service curvature, and

  64π²Δ_nr = (a_r/r − K)² − (α⁻²∂_z(αβ_r) − 2β_z a_r/α)².

The envelope keeps only a_r/r and −2β_z a_r/α. It drops three things: K, the β_r terms, and the couplings
T_nz and T_zr to the z direction.

**Exact replacement condition.**
- *General.* In C0, e_φ is always an eigenvector. The tensor is Type IV iff the discriminant of the cubic
  det(T^a_b − λδ^a_b) on the (n, z, r) block is negative.
- *Invariant (n, r) plane* (T_nz = T_zr = 0; for example β_r ≡ 0 near the point and α_rz = 0):
  Type I ⟺ |a_r/r − K| > 2|β_z a_r|/α, and Type IV ⟺ the reverse strict inequality.
- *Sub-case K = 𝒦²* (α_zz = 0, n(𝒦) = 0, i.e. uniform β_z and no along-track lapse curvature), with a_r > 0.
  Write x = r|β_z|/α and q = r a_r. Then Type IV ⟺ √(q² + q) − q < x < √(q² + q) + q. The envelope x < ½ is
  the steep-rise limit (q → ∞) of the lower edge.

**Examples** (full tensor classified at t = 0, z = 0, r = 1):

| # | Fields | Envelope 2r\|β_z\|/α | Exact | Type |
|---|---|---|---|---|
| 1 | α = exp(ln 1.5 + (r−1) + z²), β = z (convex along the track) | 1.33 (violated) | \|a_r/r − K\| = 2.56 > 1.33 | **I** (not necessary) |
| 2 | α = 0.3·e^{r−1}, β = ⅓ + z | 6.7 (violated) | x = 3.3 > 2.414 | **I** (not necessary) |
| 3 | α = 2.1·e^{r−1} or 2.3·e^{r−1}, β = ⅓ + z | 0.95, 0.87 (satisfied) | window 0.414 < x < 2.414 | **IV** (not sufficient); α = 2.5 gives I |
| 4 | α = exp(ln 10 + (r−1) − z²/2), β = z/10 (concave along the track) | 0.02 (satisfied, margin 50) | \|a_r/r − K\| = 10⁻⁴ < 0.02 | **IV** (not sufficient) |
| 5 | α = 2 + r, β = 0.45z − 0.15(r−1) − 0.425(r−1)² + 0.75(r−1)z | 0.3 (satisfied) | Δ_nr > 0 and Δ_nz > 0, but the cubic discriminant is < 0 | **IV** (coupling) |

**Method.** Symbolic discriminant; explicit fields evaluated at 40 digits; full eigen-decomposition.

**Result: HEURISTIC.** The envelope is neither necessary nor sufficient. It is exact only where the (n, r)
plane is invariant, K = 0 and β_r = 0. It errs:
- toward Type I under concavity along the track (example 4);
- even with no concavity at all, because the shift itself contributes K = 𝒦² > 0 (example 3, exact
  threshold α > 2.414 r|β_z| at q = 1);
- through (n, z) coupling (example 5).

Convexity along the track relaxes it (example 1), and so does a very low lapse (example 2).

**Derivation.**
1. Apply the block lemma to the (n, r) plane, using the Item 1 components.
2. In the invariant case, expand |a_r/r − K| > 2|β_z a_r|/α.
3. For K = 𝒦², the condition reads |1 − x²/q| > 2x. Solving the two quadratics gives the window.

---

## Item 10. I9, conformal rise is flux-free

**Statement as given.** "Where ln α and ln A rise together (a_r = b_r) the radial flux vanishes exactly even
under a moving shift that varies along the track." The inventory adds that β_r = 0 is needed.

**Exact result (C0A).** In general,

  8πT_nr = A⁻¹∂_r[(Aβ_z + βA_z − A_t)/α] − (2A)⁻¹∂_z(Aβ_r/α).

On a layer with a_r = b_r (α = F(t,z)·A):
- 8πT_nr = ∂_z(αAβ_r)/(2α²A) − n(∂_r ln A);
- 8πT_nz = −(1/(2rA²))∂_r(rA³β_r/α).

Both fluxes vanish if two conditions hold:
- (i) β_r = 0 across the rise;
- (ii) n(∂_r ln A) = 0, i.e. the rise profile is carried unchanged by the Eulerian flow. For example,
  A = A₀(t,z)e^{φ(r)}, which is static and uniform along the track across the rise.

Both conditions are needed:
- with β_r ≠ 0, the radial flux ∂_z(αAβ_r)/(2α²A) appears;
- a rise switched in time, ln A = ln A₀ + φ(t, r) with β_r = 0, gives 8πT_nr = −∂_t∂_rφ/α.

The report's "A_σ/α is r-independent" should read "(A_σ − βA_z)/α is r-independent". The report's
cancellation β_z(b_r − a_r) is the β_z part of the first term. A constant conformal factor e^{2φ} rescales
the service curvature by e^{−2φ}.

**Method.** Symbolic, with general A(t,z,r), F(t,z) and β(t,z,r), and the two counterexamples.

**Result: VERIFIED WITH ADDED HYPOTHESES** (i) and (ii).

**Derivation.**
1. Start from the momentum constraint, with K_ẑẑ = (Aβ_z + βA_z − A_t)/(αA) and K_ẑr̂ = Aβ_r/(2α) (Item 2).
2. Substitute α = FA. Then Aβ_z/α, βA_z/α and A_t/α lose their r-dependence except through β_r and
   ∂_t∂_r b, ∂_z∂_r b.

---

## Item 11. I10, the static energy and Komar balances

**Statement.** Take a static metric with β = 0 and A(z, r), α(z, r), so γ = A²dz² + dr² + r²dφ² and
√γ = Ar. Then:
- 16πρ = ³R = −2Δ⊥A/A;
- ρ√γ = −(1/8π)∂_r(r∂_rA);
- j = 0;
- 4πα(ρ + Σp_i) = D²α, with D² the Laplace–Beltrami operator of γ.

**Integral statements and fall-off.**
- *Energy, per z-slice:* ∫₀^∞ ρ√γ dr = −(1/8π)[r∂_rA]₀^∞ = 0. This needs A regular on the axis and
  r∂_rA → 0 at large r. An exactly flat exterior suffices, and so does ∂_rA = o(1/r).
- *Komar:* ∫D²α√γ d³x = ∮√γγ^{ij}∂_jα dS_i = 4πM_K. This vanishes for an exactly flat exterior, or for
  α − 1 = o(1/R) with ∂α = o(1/R²). For α − 1 ≈ −M/R it equals 4πM (Item 4). Only the full 3D integral
  vanishes; single z-slices exchange flux through ∂_z(rα_z/A).
- *Consequences.*
  - The positive and negative energies balance on every slice. If ρ ≥ 0 everywhere, then A = A(z) and the
    slice is flat.
  - A lapse maximum has D²α ≤ 0 on its crest (negative active mass) and positive active mass on its flanks.

**Method.**
- Symbolic identities.
- Numerical checks:
  - per-slice balance for A = 1 + 0.7e^{−r²−z²}: 3×10⁻⁴⁶;
  - Komar balance for a lapse ring maximum, ln α = 1.3e^{−(r−2)²−z²}, on that stretched slice: −1.1×10⁻¹⁴,
    against total positive and negative parts of 282;
  - D²α = −38.2 on the crest (r = 2) and +2.96 on the flank (r = 3.5).

**Result: VERIFIED**, with the fall-off conditions made explicit.

**Derivation.**
1. Both integrands are divergences. With √γ = Ar, ρ√γ = −(1/8π)·r·Δ⊥A = −(1/8π)∂_r(r∂_rA), and
   √γD²α = ∂_i(√γγ^{ij}∂_jα).
2. Apply the divergence theorem with the stated boundary behaviour.
3. The identity 4πα(ρ + Σp_i) = D²α is the (n,n) component of R_ab = 8π(T_ab − ½Tg_ab). For a static
   metric in static slicing, R(n,n) = D²α/α.

---

## Item 12. I11, the speed-scaling isometry

**Exact statement.**
1. **The isometry.** For C0 fields, Φ(t, x) = (ct, x) is an isometry from the metric with fields
   (cα, cβ)(ct, x) to the metric with fields (α, β)(t, x). It maps the Eulerian frame to itself, so the
   orthonormal tensors agree at corresponding points. (α, β) → (cα, cβ) is therefore an isometry exactly
   when all time dependence is compressed by c.
2. **Steady lane.** For fields F(z − vt, r), compressing time by c is the same as raising the pattern speed
   to cv. "Multiply lapse and shift by c and run the pattern at cv" is then an exact local isometry.
   Check, 2.1c → 10c on explicit profiles: agreement to 10⁻⁴⁰. Static fields scale with no change of time.
3. **Same-time scaling.** At fixed t, (α, β) → (cα, cβ) leaves every spatial-derivative term invariant.
   The only changes are:
   - 8πΔT_rr = 8πΔT_φφ = −(1 − 1/c)α⁻¹∂_t𝒦;
   - 8πΔT_zr = +(1 − 1/c)α⁻¹∂_t s/2.
4. **Ramps (what fails).** Suppose the ramp keeps its duration while lapse, shift and path speed are
   multiplied by c. Compare the result with the original ramp at the same stage (equal fraction of the lane
   speed, same comoving point). The isometric image (the ramp compressed by 1/c) reproduces the original
   tensor exactly there. The scaled ramp differs by exactly the formulas of point 3, with ∂_t replaced by
   the comoving derivative ∂_t|_ζ, i.e. by the acceleration and switching terms.
   Check, c = 100/21 on a tanh ramp of duration 1.5:
   - 8πΔT_rr = 8πΔT_φφ = −0.0438 and 8πΔT_zr = +0.0394, matching the formula to 5×10⁻⁴¹;
   - the compressed ramp matches to 10⁻⁴⁰.
5. **Regions.** The isometry holds where both the lapse and the shift are scaled. In uniform-shift regions
   the tensor is the pure-lapse tensor of Item 3. It depends only on the spatial profile of α, up to a
   constant factor, and on no time derivative. It therefore changes only where the shape of the lapse
   profile changes (the hole, the outer falls, the cone), and stays Type I there. Regions with uniform α
   and β are flat for any values. The lapse must be scaled everywhere the shift is non-uniform. The map is
   never a global isometry, since the exterior lapse stays 1.

**Method.** Symbolic jet scaling of all ten components; the explicit steady lane and ramp at 40 digits.

**Result: VERIFIED WITH CORRECTED HYPOTHESES.** The isometry is exact for steady lanes (pattern speed
scaled) and for static fields. During ramps the exact correction is point 4.

**Derivation.** Φ*g = −c²α(ct,x)²dt² + (dz + cβ(ct,x)dt)² + …, and Φ*n = n. For the same-time formula,
𝒦 and s are invariant under (α, β) → (cα, cβ), and n(f) = α⁻¹(∂_t − β∂_z)f loses a factor c on its ∂_t part.

---

## Item 13. General 3+1 lemmas

**(a) Zero momentum ⇒ Type I; static slicing.** For any metric, j = 0 gives T^μ_νn^ν = −ρn^μ. The remaining
block is S^i_j, symmetric with respect to the positive-definite γ_ij, hence diagonalizable with real
eigenvalues. So T is diagonal in an orthonormal tetrad containing n: Type I.

A static metric in static slicing (β = 0, ∂_tγ = 0) has K_ij = 0, so j = 0 by the momentum constraint.
Moreover ρ = ³R/16π and 8πS_ij = ³G_ij + (γ_ijD²α − D_iD_jα)/α, also for a time-dependent lapse.

Checks:
- symbolic, for a general diagonal static slice with α(t,x,y,z);
- numerical: five random j = 0 tensors are Type I, and ρ = S = 0 with j = e_x is Type IV.

**Result: VERIFIED.**

**(b) Momentum and vorticity (flat slices, general α(t,x) and β^i(t,x)).** With σ_ij = ∂_(iβ_j),
θ = ∇·β, ω = ∇×β and j_i = −T(n,e_i):

  8πj = −(∇×ω)/(2α) − (σ − θ𝟙)·∇α/α².

With unit lapse, 8πj = −½∇×∇×β at every instant. The identity holds for time-dependent shifts too, since
K_ij involves no time derivative of β on flat static slices.

Comparison with Le 2026b (Lemma 2), stated for time-independent, flat, unit-lapse slices:
- the magnitude 8π|j| = ½|∇×(∇×β)| agrees;
- "j ≡ 0 iff gradient plus rigid rotation" follows for bounded vorticity on ℝ³. From ∇×ω = 0 and ∇·ω = 0,
  ω is harmonic and bounded, hence constant (Liouville), so β − ½ω×x is curl-free on ℝ³;
- with β = −v, this reproduces SSV's flux vector (1/16π)∇×∇×v, up to the sign convention of their flux.

Extra terms for a non-unit lapse:
- the vorticity term is reduced by 1/α;
- a new term −(σ − θ𝟙)∇α/α² appears. A rigid rotation still gives j = 0 for any lapse (σ = θ = 0), while
  a gradient shift β = ∇χ carries 8πj = −(∇∇χ − Δχ𝟙)∇α/α².

**Result: VERIFIED**, and extended to time-dependent shifts and non-unit lapse.

**(c) The Santiago–Schuster–Visser form.** With any lapse:

  16πα²ρ = θ² − σ:σ = ∂_i(β_iθ − β_j∂_jβ_i) − ½ω·ω.

Hence ∫α²ρ d³x = −(1/32π)∫ω² d³x ≤ 0 (unit lapse: ∫ρ = −∫ω²/32π; Shoshany–Snodgrass for general lapse).
This holds when the boundary flux of β_iθ − β_j∂_jβ_i vanishes: β = o(R^{−1/2}) with ∂β = o(R^{−3/2}), or
compact support. The flux through a sphere is O(R²|β||∂β|).

Checks:
- numerical, for a Gaussian-localized general shift: ∫ρ = −0.0763061566718 = −(1/32π)∫ω², to 12 digits;
- **the boundary case fails**: with unit lapse and β = √(2m/r) r̂, m = Mr³/(r²+a²)^{3/2} (β ~ r^{−1/2}),
  ω = 0 while ∫ρ d³x = M > 0. The fall-off quoted in the inventory for Shoshany–Snodgrass,
  "β = O(r^{−1/2})", must read o(r^{−1/2}).

**Result: VERIFIED** (with the fall-off o(R^{−1/2})).

**(d) Shoshany–Snodgrass eq. 4.3.** On flat slices, 16πρ = [(∂_iβ^i)² − ∂_(iβ_j)∂_(iβ_j)]/α², verified from
G(n,n) for general α and β^i. For β = β(t,x,y,z)ê_z it reduces to ρ = −|∇⊥β|²/(32πα²), because
θ² − σ:σ = −½(β_x² + β_y²).

**Result: VERIFIED.**

**(e) Energy quadratic in speed.** On flat slices ρ contains no time derivative, so for β = v·b(x) with a
v-independent lapse, ρ ∝ v² pointwise and ∫ρ ∝ v² on any fixed domain (Le 2026b, Lemma 4).

For a C0 pattern moving at v, with the lapse profile fixed and the shift equal to v·b(z − vt, r), each
component is a polynomial in v:
- ρ ∝ v²;
- T_nz and T_nr ∝ v;
- T_zz, T_rr, T_φφ and T_zr each have a v⁰ part (lapse) and a v² part.

The speed-scaling isometry (Item 12) breaks the fixed-lapse premise.

**Result: VERIFIED.**

**Methods (13).** Symbolic in all cases; the general-shift engine run covers α(t,x,y,z) and three shift
components. A spectral quadrature is used for the integral check.

---

## Summary

| Item | Inventory ID | Statement (short) | Result |
|---|---|---|---|
| 4 | 02 §2.1 lemma | Every non-constant lapse on flat slices with α → 1 violates the NEC | **VERIFIED WITH CORRECTED HYPOTHESES**: shift Killing on the *whole* slice; α bounded above; no fall-off rate needed. The Komar argument needs M_K = 0; the plane (2D Liouville) proof covers all bounded lapses and localizes the violation. Counterexamples given |
| 7 | I6 (Type IV clause) | Type IV wherever \|Δ⊥β\| > β_r² | **FALSE** in general (static counterexample, Type I); true where the (n,z) plane is invariant |
| 9 | I8 | α > 2r\|β_z\| for Type I | **HEURISTIC**: neither necessary nor sufficient (five explicit examples); exact criteria given |
| 12 | I11 | (α,β) → (cα,cβ), t → t/c is an isometry | **VERIFIED WITH CORRECTED HYPOTHESES**: exact with time compression (steady lane, static); exact ramp correction given |
| 10 | I9 | Conformal rise is flux-free | **VERIFIED WITH ADDED HYPOTHESES**: β_r = 0 across the rise and n(∂_r ln A) = 0 |
| 2 | I1 (A ≠ 1) | ρ = −(Aβ_r/α)²/32π | **VERIFIED WITH CORRECTED FORMULA**: ρ = −(Aβ_r/α)²/32π − Δ⊥A/(8πA); the report form is exact for A(t,z) |
| 3 | I2, I18 | Pure lapse: ρ = j = 0, 8πT_ij = (δΔα − ∂∂α)/α, Type I; directional form | **VERIFIED WITH ADDED HYPOTHESES**: uniform on a time interval (extends to Killing shifts); the radial-ray integral needs α = α(r) |
| 6 | I4c (sign) | Convex lapse ⇒ K < 0 ⇒ p_r > 0 | Formula **VERIFIED**; sign reading **VERIFIED WITH ADDED HYPOTHESIS** α_zz/α > 𝒦² − n(𝒦) |
| 7 | I5 | 8πT_nr ≈ −a′β_z/α, 8π(ρ+p_r) ≈ a′/r | **VERIFIED WITH ADDED HYPOTHESES**: exact for β_r ≡ 0 locally, with −K restored |
| 13c | SS fall-off (as quoted) | ∫N²ρ ≤ 0 for β = O(r^{−1/2}) | **VERIFIED WITH CORRECTED HYPOTHESIS**: needs β = o(r^{−1/2}); counterexample at r^{−1/2} gives ∫ρ = M > 0 |
| 1 | §3.2 | Complete C0 tensor (A = 1) | **VERIFIED** (all ten components and null sums) |
| 2 | I1 (A ≡ 1) | ρ = −(β_r/α)²/32π | **VERIFIED** |
| 5 | I3, I26, I20 | Uniform fields flat; aging α_c/v; light speed −β ± α/A; static observers iff α > A\|β\| | **VERIFIED** |
| 6 | I4 | Product: 8πT = diag(K_Σ, −K_Σ, −K, −K); min null energy min(0, (K_Σ−K)/8π) | **VERIFIED** |
| 7 | I5c, I6 identity | Exact flux forms; 8πT(n±e_z) = −(β_r² ± Δ⊥β); proper-shear flux with stretch | **VERIFIED** |
| 8 | I7 | Doubly warped Hessian identity | **VERIFIED** |
| 11 | I10 | Static energy and Komar balances | **VERIFIED** (fall-off explicit) |
| 13a | — | j = 0 ⇒ Type I; static ⇒ K_ij = 0 | **VERIFIED** |
| 13b | Le 2026b | 8πj = −½∇×ω (unit lapse); gradient plus rigid rotation | **VERIFIED**; extended to time-dependent shifts and to general lapse |
| 13c | SSV | 16πρ = div − ½ω²; ∫ρ = −∫ω²/32π | **VERIFIED** (fall-off o(R^{−1/2})) |
| 13d | SS eq. 4.3 | Reduces to −\|∇⊥β\|²/(32πα²) | **VERIFIED** |
| 13e | Le 2026b L4 | Energy quadratic in speed | **VERIFIED** (lapse independent of v) |
| 0 | — | Engine: PG Schwarzschild, FRW, Alcubierre eq. 19 | passed |
