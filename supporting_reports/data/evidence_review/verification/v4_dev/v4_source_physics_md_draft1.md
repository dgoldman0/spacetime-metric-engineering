# V4. Source physics: quantum inequalities, Casimir cavities, curvature-coupled scalars, the trace anomaly, scaling, and the source identities Q1–Q13

Verification record for the textbook, 2026-09-26.

- Script: `v4_source_physics.py` (sympy, mpmath, numpy/scipy; written from scratch, nothing imported
  or copied from the repository). Run log: `v4_source_physics_run.log`.
- Run: `nice -n 10 env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 v4_source_physics.py`
  (one process, about 200 s; individual sections can be selected, e.g. `... v4_source_physics.py qi casimir`).
- Outcome: **190 of 190 checks pass.** Two consecutive full runs produce identical output apart
  from the timing lines. Check labels quoted below appear verbatim in the log.
- The one `RuntimeWarning: overflow` line in the log is benign: `cosh(λ)²` overflows for λ > 355 in
  the long-ray integration, and the potential correctly evaluates to 0 there.
- Physical constants come from `scipy.constants` (the CODATA set shipped with scipy 1.16.2), so no
  constant is typed from memory; ℓ_P = 1.616255×10⁻³⁵ m.
- The repository was read only for the exact wording of the statements: SOURCE_SCALING_TEST.md,
  QUANTUM_ESTIMATES_PASS.md, DEMAND_CENSUS.md, and for Q1–Q13 the reports named in
  knobs_throat_era.md §5.4.

Paths used below: `T` = `/tmp/claude-1000/-media-projectspace-active-rail-refined-design-base/a768759a-f000-4d67-a799-86d86986da85/scratchpad/textbook`,
`S` = its parent scratchpad directory.

**Conventions** (T/05_STRUCTURE.md): signature (−,+,+,+); MTW Riemann; G_ab = 8πT_ab with G = c = 1 in
the geometric parts; ħ explicit in the quantum parts; ℓ_P = (ħG/c³)^{1/2}. A demand in rail units
converts to SI as stress × c⁴/(GL²) and energy × c⁴L/G. The conversion constant of the throat-era
reports, η = 2.4127904527582454×10⁻⁵, is (ℓ_P/L)² at the recorded rail unit L = 203.58 ℓ_P ("204 ℓ_P").
It converts ħc/L⁴ into c⁴/(GL²).

---

## 1. I21 — Quantum inequality, field count and species length

### 1a. The Fewster–Roman Gaussian constant

**Statement.** For the free, massless, minimally coupled real scalar in 4D Minkowski space, an inertial
worldline with 4-velocity u, a constant null vector k and any Hadamard state for which the left side
converges absolutely:

  ∫⟨:T_ab:k^a k^b⟩ g(τ)² dτ ≥ −((u·k)²/12π²) ∫ g''(τ)² dτ  (Fewster–Roman Eq. III.10, ħ = c = 1).

For g(τ) = (2πτ₀²)^{−1/4} e^{−τ²/4τ₀²} (Eq. III.12), g² is a normalized Gaussian of **standard
deviation τ₀**, and the bound is −(u·k)²/(64π²τ₀⁴) (Eq. III.13). With ħ and c restored, the bound is
−ħc (u·k)²/(64π² (cτ₀)⁴) in J/m³.

**Method.** Symbolic integration of ∫g², ∫τ²g², ∫(g'')². Independent re-derivation of the III.6–III.10
chain: the angular integral ∫₋₁¹(1−cosθ)² d cosθ = 8/3, the α-integral ∫₀^u ω³dω = u⁴/4, and Parseval
for the Fourier transform ĝ(u) = ∫g e^{iuτ}dτ.

**Result: VERIFIED.** The checks "int g''^2 dtau = 3/(16 tau0^4)", "Eq. (III.10) with Gaussian ->
-(u.k)^2/(64 pi^2 tau0^4)", "angular + alpha integrals give the 1/(12 pi^3) prefactor" and "Parseval
step" all pass. The paper's sentence after Eq. III.12 says g² has "variance τ₀". The displayed g has
variance τ₀², i.e. standard deviation τ₀ (check "g^2 has standard deviation tau0"), and the constant
64π² holds for the standard deviation. The book should state standard deviation.

**Derivation sketch (book).** With s = τ/τ₀, g'' = (2πτ₀²)^{−1/4} τ₀⁻² (s²/4 − 1/2) e^{−s²/4}. Hence
∫g''² dτ = (2π)^{−1/2} τ₀⁻⁴ ∫(s²/4 − 1/2)² e^{−s²/2} ds = (2π)^{−1/2} τ₀⁻⁴ · √(2π)(3/16 − 1/4 + 1/4)
= 3/(16τ₀⁴). Multiplying by 1/12π² gives 1/(64π²τ₀⁴).

**Scope from the source (Theorem III.1).** The inequality in its general form holds along any smooth
timelike curve (not necessarily a geodesic) in any globally hyperbolic spacetime, for the Klein–Gordon
field of mass m ≥ 0, with normal ordering relative to a Hadamard reference state. The closed form III.13
is the Minkowski, inertial, constant-null-vector, Minkowski-vacuum evaluation.

**Literature checked.** `T/inventory/lit_foundations_evidence/gr-qc_0209036.txt`: Theorem III.1 at
lines 563–590, Eqs. III.4–III.10 at lines 590–681, Eqs. III.12–III.13 at lines 690–700. The same text is
in `S/arx/pdf/gr-qc_0209036v2.txt`.

### 1b. The field-count requirement N ≥ 64π² d τ₀⁴ (L/ℓ_P)² ≡ Q (L/ℓ_P)²

**Statement (with the hypotheses made explicit).** Let a demand of fixed shape be given in rail units
at unit length L. Let d be the **window-averaged null deficit**:

  d = −∫T(k,k) g² dτ,

evaluated along a static (source-unit) worldline, with k held fixed along the window, normalized by
u·k = −1, and T in units c⁴/(GL²). Let τ₀ be the **standard deviation of the Gaussian g², in units of
L/c**. Suppose this deficit is supplied by N free, massless, minimally coupled scalar fields in a
Hadamard state, and the flat-space bound 1a applies, i.e. cτ₀ is short compared with the local
curvature radius and with the inverse proper acceleration of the worldline. Then

  N ≥ 64π² d τ₀⁴ (L/ℓ_P)² ≡ Q (L/ℓ_P)².

**Method.** Symbolic, with ħ, c, G, L kept. The deficit is d c⁴/(GL²). The per-field bound is
ħc/(64π²(τ₀L)⁴). N fields give N times the per-field bound. The ratio simplifies to
64π² d τ₀⁴ L²c³/(ħG) (check "N >= 64 pi^2 d tau0^4 (L/l_P)^2").

**Result: VERIFIED WITH HYPOTHESES MADE EXPLICIT.** The algebra and the constant are exact. The
statement needs three hypotheses that the inventory line omits:
1. **Field species.** N counts free massless minimally coupled scalars, the field of Theorem III.1.
   Other free fields obey QEIs with different constants, so for them N is a scalar-equivalent count.
2. **The deficit is window-averaged.** SOURCE_SCALING_TEST.md averages d over the Gaussian ("the deficit
   history is averaged over the Gaussian").
3. **Curved-spacetime use is a premise.** Applying the flat-space bound in curved spacetime is Ford and
   Roman's premise: the bound holds in regions small compared with the curvature radius and the distance
   to boundaries, with τ₀ = f × (smallest local scale) and f ≪ 1. It is argued there, not proved; the
   inverse-acceleration condition extends it to accelerated worldlines.

**Derivation sketch (book).** The sampled null energy of N independent fields is bounded below by the sum
of the individual bounds, −Nħc/(64π²(cτ₀)⁴). A sustained deficit of d·c⁴/(GL²) over the window
therefore needs N ħc/(64π² τ̂₀⁴ L⁴) ≥ d c⁴/(GL²), which rearranges to N ≥ 64π² d τ̂₀⁴ L²c³/(ħG).
Since c³/(ħG) = 1/ℓ_P², this is N ≥ 64π² d τ̂₀⁴ (L/ℓ_P)².

**Literature checked.** `T/inventory/lit_foundations_evidence/gr-qc_0209036.txt` (as in 1a).
`T/inventory/lit_foundations_evidence/gr-qc_9510071.txt` (Ford–Roman 1996): curved-spacetime premise at
lines 44–55 and 226–236; τ₀ = f r_m with f ≪ 1 (e.g. f ≈ 0.01) at lines 599–608; restriction to the
minimally coupled scalar and the "not yet done" extension to other fields at lines 330–336.

### 1c. The stated Q values (0.013 at f = 0.1; 3×10⁻⁶ at f = 0.01)

**Statement.** On the staged D-lap design, the maximum over the main-demand zones is Q = 0.013 at sampling
fraction f = 0.1 and 3×10⁻⁶ at f = 0.01 (SOURCE_SCALING_TEST.md:116–155).

**Method.** Three checks:
1. Q = 64π² d τ₀⁴ at each tabulated governing point, with the two-significant-figure rounding intervals
   of d and τ₀ propagated.
2. The field-count table (N at five unit lengths per column) inverted for Q, intersecting the rounding
   intervals of all entries.
3. Monotonicity in f: when τ₀ ≤ f × (local scale), Q(f)/f⁴ cannot increase with f.

**Result: DESIGN-SPECIFIC (internally consistent within rounding).**

| Zone (f = 0.1) | 64π² d τ₀⁴, central | Range from rounding | Stated |
|---|---:|---:|---:|
| service region / inner band | 0.00522 | 0.00461–0.00589 | 0.0051 |
| sheath rise | 0.00729 | 0.00622–0.00851 | 0.0065 |
| sheath plateau | 0.00815 | 0.00729–0.00909 | 0.0077 |
| outer falls | 0.0147 | 0.0134–0.0160 | 0.013 |

- **Field-count table.** Every entry in each column fits one Q: [0.01334, 0.01345] for f = 0.1 and
  [3.00, 3.24]×10⁻⁶ for f = 0.01. These round to the stated 0.013 and 3×10⁻⁶; the zone table gives
  3.1×10⁻⁶.
- **Outer-falls row.** It is consistent only at the low edge of its rounding interval, near
  τ₀ ≈ 0.235 and d ≈ 0.0070. That matches the report's remark that sampled averages sit up to 0.5%
  below the pointwise values.
- **Faint-tail row.** It cannot be reproduced from its pointwise inputs: 64π² × 6×10⁻⁷ × 14.8⁴ = 18,
  against the stated 0.030. There the window-averaged deficit of a brief pulse (the quantum-interest
  regime) enters, and the table does not give that average. This row is not checkable from the report.
- **Monotonicity.** Q(0.01) = 3.1×10⁻⁶ ≥ 10⁻⁴ × Q(0.1) = 1.3×10⁻⁶, as required.

The values are measurements on one design. The book may quote them only in a labelled "measured on one
design" box.

**Literature checked.** None needed. Inputs are from `SOURCE_SCALING_TEST.md` (repository, read-only).

### 1d. Species length ℓ* = √Q L

**Statement.** N light species bring gravity to strong coupling at ℓ* ≈ √N ℓ_P. With N = Q(L/ℓ_P)²,
this gives ℓ* = √Q L. The report derives L ≤ 52 μm/√Q from the absence of deviations from Newtonian
gravity down to 52 μm.

**Method.** Arithmetic, plus a reading of the local sources for the species relation.

**Result: VERIFIED (algebra); ORDER-OF-MAGNITUDE (physics).** The algebra ℓ* = √N ℓ_P = √Q L is exact,
and the numbers reproduce:
- ℓ*/L = 0.116 (f = 0.1), 0.173 (faint tail, Q = 0.030) and 0.00176 (f = 0.01);
- L_max = 0.4475 mm, 0.300 mm and 2.95 cm.

The species relation itself holds only up to O(1) factors:
- The local sources give it as Λ_G ≈ M_P/√N and G_N ∼ ℓ_UV²/N, both "≈" or "∼" statements.
- If M_P is the reduced Planck mass, ℓ* is larger by √(8π) = 5.0.

The bound L ≤ 52 μm/√Q rests on two assumptions. The strong-coupling length must lie below the shortest
length at which gravity has been tested. The 52 μm figure (Lee et al. 2020) is not in the local texts.

**Book form.** ℓ* ∼ √N ℓ_P (O(1) factors model-dependent); a quantum-supplied design of fixed shape has
ℓ*/L = √Q independent of scale.

**Literature checked.**
- `T/arx/raw_0706.2050.html` (Dvali, abstract: "lower bound on the Planck mass … given by NΛ²").
- `T/arx/raw_0710.4344.html` (Dvali–Redi, abstract: "Λ_G ≈ M_Planck/√N").
- `T/inventory/lit_foundations_evidence/1807.03808.txt` lines 844–848 (Freivogel–Krommydas:
  "G_N ∼ ℓ_UV²/N").
- Summaries in `T/inventory/lit_foundations.md` §4.19–4.20.
- Only the Dvali abstracts are local; the full texts are not saved.

---

## 2. I21 — Casimir cavities

### 2a. The ideal-mirror null deficit along the normal

**Statement.** Between ideal (perfectly conducting) parallel plates a distance a apart, the renormalized
electromagnetic vacuum stress is uniform:

  (ρ, p_⊥, p_∥, p_∥) = C(−1, −3, +1, +1),  C = π²ħc/(720a⁴).

The null energy along the normal is therefore ρ + p_⊥ = −4C = **−π²ħc/(180a⁴)**.

For comparison:
- A conformally coupled (ξ = 1/6) scalar with Dirichlet or Neumann plates has half these values:
  C = π²ħc/(1440a⁴), and the null deficit is π²ħc/(360a⁴).
- A minimally coupled scalar has the same p_⊥, but its energy density depends on position (it differs by
  (1/6)∂_z²⟨φ²⟩, divergent at the plates), so it has no uniform deficit.

**Method.** Two independent regularizations:
1. **Zeta/dimensional regularization.** Per mode, (1/2)∫d²k/(2π)² (k² + M²)^{1/2} = −M³/12π; the sum
   uses ζ(−3) = 1/120, two polarizations for n ≥ 1, and a scale-free n = 0 mode.
2. **The Lifshitz scattering formula**, (1/4π²)∫κ² ln(1 − r₁r₂e^{−2κa}) dκ with r₁r₂ = 1, integrated
   numerically.

Then p_⊥ = −∂(E/A)/∂a and p_∥ follows from tracelessness.

**Result: VERIFIED** for the electromagnetic field, which is the case the report uses ("ideal mirrors",
plasma-frequency mirrors). Checks: "EM (perfect conductors): E/A = -pi^2 hbar c/(720 a^3)", "EM null
deficit along the normal = pi^2 hbar c/(180 a^4)", "conformal scalar null deficit … = pi^2 hbar c/(360 a^4)".
The result matches the local literature values exactly.

**Derivation sketch (book).** Modes k_z = nπ/a give E/A = 2 Σ_{n≥1} (−(nπ/a)³/12π) = −(π²/6a³) ζ(−3)
= −π²ħc/(720a³). Then ρ = (E/A)/a = −C and p_⊥ = −d(E/A)/da = −3C. Tracelessness gives p_∥ = (ρ − p_⊥)/2
= +C, so ρ + p_⊥ = −4C.

**Literature checked.**
- `S/wh/txt/1907.03623v1.txt` (Garattini 2019), Eqs. (1)–(4) and (11), lines 27–47 and 101–110:
  E = −ħcπ²S/(720a³), P = −3ħcπ²/(720a⁴), ρ = −ħcπ²/(720a⁴), T^{μν} ∝ η^{μν} − 4ẑ^μẑ^ν.
- `S/wh/txt/MTY1988_ocr.txt` lines 122–133 (Morris–Thorne–Yurtsever 1988: τ = 3p = −3ρ = (3π²/720)ħ/s⁴).
- Brown–Maclay 1969 itself is not saved locally.

### 2b. The matching gap a = 0.58 √(ℓ_P L)

**Statement.** The gap at which the EM ideal-mirror deficit equals the demand's peak static-frame null
deficit, d_peak = 0.48 c⁴/(GL²) with u·k = −1 (SOURCE_SCALING_TEST.md:63–65), is

  a = (π²/(180 d_peak))^{1/4} √(ℓ_P L) = 0.5814 √(ℓ_P L).

**Method.** Solve π²ħc/(180a⁴) = d_peak c⁴/(GL²), then reproduce the gap table.

**Result: VERIFIED.** The coefficient is 0.58136; the scalar value would give 0.489. The table rows at
204 ℓ_P, 1 μm, 1 mm, 1 m and 1 km reproduce within 5% (rounding):
- at 1 m, a = 2.34×10⁻¹⁸ m, a/ƛ_C = 6.05×10⁻⁶ and 2πħc/a = 530 GeV;
- at 1 km, 17 GeV.

The input d_peak = 0.48 is design-specific.

**Derivation sketch.** a⁴ = π²ħGL²/(180 d_peak c³) = (π²/180 d_peak) ℓ_P² L².

**Literature analogue checked.** `S/wh/txt/MTY1988_ocr.txt` lines 138–141 performs the same matching for
a wormhole throat r₀ (s ∝ (r₀ℓ_P)^{1/2}).

### 2c. The "~10⁷ mirror overhead"

**Statement (report).** Model the mirror as an electron gas with plasma frequency ω_p = k·2πc/a, one skin
depth c/ω_p thick. Its energy per unit area exceeds the cavity's null deficit per unit area,
π²ħc/(180a³), by the following amounts:
- **Non-relativistic electrons** (a ≳ 113 k ƛ_C): 90k/(π²α)·(a/ƛ_C)² ≈ 1250k(a/ƛ_C)², at least 1.6×10⁷ in
  that regime.
- **Ultra-relativistic electrons** (ω_p² = (4α/3π)c²k_F², energy density ħck_F⁴/4π²): 1.2×10⁷k³,
  independent of the gap.

The regimes "meet within a factor of 1.4", and rails below 3.5×10¹⁴ m (2,300 AU) sit in the
ultra-relativistic regime.

**Method.** Symbolic derivation in Gaussian units (e² = αħc):
- the plasma frequency from the long-wavelength Vlasov dielectric, ω_p² = 4πe² ∫d³p f₀ (1/3)∇_p·v, whose
  non-relativistic limit is 4πne²/m and whose ultra-relativistic limit is (4α/3π)c²k_F²;
- the degenerate-gas relations n = k_F³/3π² and u = ħck_F⁴/4π², derived from the Fermi integrals;
- the regime boundary p_F = m_e c.

**Result: ORDER-OF-MAGNITUDE — the arithmetic is exact.**
- Non-relativistic ratio: (90k/π²α)(a/ƛ_C)², with 90/(π²α) = 1249.6.
- Boundary: a_c = √(3π³/α) k ƛ_C = 112.9 k ƛ_C.
- Ultra-relativistic ratio: (405π/2)k³/α² = 1.195×10⁷ k³.
- At a_c the two ratios are exactly in the proportion **4/3** (1.593×10⁷ vs 1.195×10⁷).
- The ultra-relativistic regime covers rails below 3.48×10¹⁴ m = 2,326 AU.

Assumptions of the argument:
1. The mirror is a cold, degenerate gas of unit-charge carriers (electrons). For carriers of charge Ze,
   the ultra-relativistic ratio before neutralization scales as Z⁻⁴, and heavier carriers raise the
   non-relativistic ratio as (M/m_e)². At the gaps required for metre-scale rails (≪ a proton radius),
   no nuclei survive, so the electron gas is the relevant idealization.
2. Reflection requires cavity modes below ω_p, and the mirror is at least one skin depth c/ω_p thick.
3. The mirror's cost is its energy per area. Its ρ + p ≥ ρ, so this comparison is conservative for the
   null-energy balance. Only one skin depth of one plate is counted, and ions or positrons add more.
4. The ideal (perfect-conductor) deficit is used. A plasma mirror with ω_p ≈ 2πc/a gives a smaller
   deficit, which strengthens the conclusion.
5. k ≥ 1 is a free order-one factor. The ratios grow as k to k³.

**Book form.** For electron-gas mirrors, the positive energy of the thinnest reflecting layer exceeds the
cavity deficit it bounds by ≳ 10⁷ at every gap. This is an order-of-magnitude exclusion under
assumptions 1–5, not a theorem.

**Literature context.** `S/wh/txt/MTY1988_ocr.txt` lines 148–162 makes the analogous plate-mass argument
(plates' mass-to-charge ratio versus the electron Compton wavelength). No local text contains the report's
plasma-mirror estimate; it is the report's own argument, rederived here.

---

## 3. I21 — Curvature-coupled scalars

### 3a. F″ ≤ 8πT(k,k)F

**Statement.** Take the action (1/16π)∫F(φ)R − ½(∇φ)² − V(φ) plus matter (G = 1), with any F. The case
F = 1 − 8πξφ² is the ξRφ² coupling. The metric field equation is

  F G_ab = 8π(T^φ_ab + T^m_ab) + ∇_a∇_bF − g_ab □F,  T^φ_ab = ∇_aφ∇_bφ − g_ab(½(∇φ)² + V).

Along an affinely parametrized null geodesic with tangent k, write F″ = d²F/dλ² and T ≡ G/8π for the
demanded tensor:

  F″ = 8πT(k,k)F − 8π[(k·∇φ)² + T^m(k,k)] ≤ 8πT(k,k)F,

provided the kinetic term is healthy, so that (k·∇φ)² ≥ 0, and the matter obeys the NEC.

**Method.**
1. The tensor E_ab = F G_ab + g_ab□F − ∇_a∇_bF was checked against the Euler–Lagrange derivatives of the
   second-order Lagrangian √−g F R. The check used the static spherical family
   ds² = −e^{2Φ}dt² + e^{2Λ}dr² + e^{2Ψ}r²dΩ² with arbitrary Φ(r), Λ(r), Ψ(r), F(r). Symmetric
   criticality holds for this family, and EL_Φ = −2√−g E^t_t, EL_Λ = −2√−g E^r_r and
   EL_Ψ = −2√−g(E^θ_θ + E^φ_φ) hold identically.
2. k = (e^{−2Φ}, e^{−Φ−Λ}, 0, 0) was checked to be null and affinely geodesic, and
   k^a k^b ∇_a∇_bF = d²F/dλ² was verified symbolically.
3. Contracting the field equation with k k gives the identity.

**Result: VERIFIED.** The inequality holds for any F(φ); it does not need F > 0.

**Derivation sketch (book).** Vary √−g F R: δ(√−g F R) = √−g(F G_ab + g_ab□F − ∇_a∇_bF)δg^{ab}. Contract
the field equation with k^a k^b: the g_ab□F term drops because g(k,k) = 0. The affine condition
k^b∇_bk^a = 0 gives k^a k^b∇_a∇_bF = F″. Finally T^φ(k,k) = (k·∇φ)² ≥ 0 and T^m(k,k) ≥ 0.

### 3b. Sturm comparison: F vanishes by the first zero of ψ″ = 8πT(k,k)ψ

**Statement (with the entry condition made explicit).** Let the null geodesic be complete and enter the
structure from a flat region extending to past infinity. Let ψ solve ψ″ = 8πT(k,k)ψ with ψ = 1 and ψ′ = 0
at the entry point λ₀. Then any C² function with F > 0 and F″ ≤ 8πT(k,k)F along the ray satisfies:

- F(λ) ≤ F(λ₀)ψ(λ) up to the first zero λ₁ of ψ, so F must vanish in (λ₀, λ₁]. If ψ stays positive
  through the structure but leaves with ψ′ < 0, its zero lies in the flat future and the same holds there.
- Equivalently, no F > 0 exists on the complete ray when −d²/dλ² + 8πT(k,k) has a bound state
  (Allegretto–Piepenbrink). For compactly supported T(k,k), the number of zeros of ψ on the ray equals
  the number of bound states. The count is invariant under λ → cλ, 8πT(k,k) → 8πT(k,k)/c², so it is
  independent of the normalization of k and of the scale L.

**Method.**
- **Lemma.** On a flat past where F″ ≤ 0 and F > 0, a positive slope would extrapolate to F < 0.
  Hence F′(λ₀) ≤ 0, so the Wronskian W = F′ψ − Fψ′ satisfies W(λ₀) ≤ 0. Since W′ = F″ψ − Fψ″ ≤ 0 while
  ψ > 0, we get (F/ψ)′ = W/ψ² ≤ 0.
- **Numerics.** Five profiles 8πT(k,k) were tested:
  - Pöschl–Teller wells with 1, 2 and 3 bound states;
  - a positive core flanked by two negative "falls", a lapse-hill-like profile with 2 bound states;
  - a purely positive profile.
- For each profile:
  - The zero count of ψ was compared with the number of negative eigenvalues of a finite-difference
    Hamiltonian on a large Dirichlet box.
  - Twelve random admissible F per profile (F″ = qF − s, s ≥ 0, F′(λ₀) ≤ 0) were integrated, and each
    was checked to hit zero before λ₁.
  - W was checked to be non-increasing.
- Two further checks: no entry slope in [−1, 2] from the flat past keeps F > 0 through a bound-state
  ray; and a segment that starts inside the structure with F′ = +5 does keep F > 0.

**Result: VERIFIED WITH HYPOTHESES MADE EXPLICIT.**
- The inventory sentence omits the flat-past entry. The comparison needs F′(λ₀) ≤ 0, which a complete
  ray from flat past infinity supplies automatically.
- A zero-energy resonance (ψ′ → 0 exactly at +∞) is the borderline case of the zero/bound-state count.
- All numerical checks pass. Zero counts equal bound-state counts: 1, 2, 3, 2 and 0. For example the
  Pöschl–Teller V₀ = 3.75 well has eigenvalues −2.25 and −0.25.
- Every admissible F vanished before ψ's first zero; the largest value of λ_{F=0} − λ_{ψ=0} was −0.006.

**Derivation sketch (book).** W′ = F″ψ − Fψ″ ≤ 8πT(k,k)Fψ − F·8πT(k,k)ψ = 0 on ψ > 0, and W(λ₀) = F′(λ₀) ≤ 0.
Therefore F/ψ ≤ F(λ₀) on [λ₀, λ₁), and F → 0 as ψ → 0. By the Sturm oscillation theorem, the zeros of the
zero-energy solution count the bound states.

**Literature checked.** None available locally:
- Barceló–Visser 2000 (CQG 17, 3843) and Butcher 2015 (PRD 91, 124031) are **not saved**.
- Local context only: the Barceló–Visser 2002 essay abstract and the Fliss–Freivogel–Kontou–Pardo Santos
  2023 abstract (arXiv:2309.10848), both in
  `T/inventory/lit_foundations_evidence/arxiv_abstract_pages_parsed_2026-09-26.txt`. The latter says that
  when the field range is below the EFT cutoff, ANEC holds, consistent with F staying away from zero.
- `S/wh/txt/2405.05963v2.txt` (Kontou 2024) cites Barceló–Visser 2000 (ref. 16) but does not reproduce
  the result.

The derivation above stands on its own; the literature cross-check is **not possible locally (flag)**.

---

## 4. I22 — Trace anomaly: normalization and per-species coefficients

**Statement.** For a conformal field in any state, with R² counterterms omitted:

  ⟨T^μ_μ⟩ = (c W² − a E)/(16π²) · ħc/L⁴,

with W² = C_abcd C^abcd, E = R_abcd R^abcd − 4R_ab R^ab + R², and the curvatures in units of 1/L⁴. The
per-species coefficients (a, c) are:
- conformally coupled real scalar: (1/360, 1/120);
- two-component Weyl fermion: (11/720, 1/40);
- Maxwell field: (31/180, 1/10).

On Ricci-flat backgrounds the scalar value is K/(2880π²), with K the Kretschmann scalar.

**Method.**
1. **Normalization against the local literature.** Using W² = Riem² − 2Ric² + R²/3 (itself checked on
   S²×S² from the Weyl tensor), (cW² − aE)/16π² with the scalar values equals
   (Riem² − Ric²)/(2880π²) identically. This is Ford–Roman Eq. (10) without its □R term. The trace of
   the R²-counterterm tensor H⁽¹⁾ of Ford–Roman Eq. (11) is −6□R, so a finite R² term changes only the
   □R coefficient.
2. **Independent spectral (ζ-function) determination of (a, c, d) for all three species.** d is a
   possible R² coefficient.
   - Under a constant rescaling g → λ²g, ζ_{λ²g}(s) = λ^{2s}ζ_g(s). This gives ∫√g⟨T^μ_μ⟩ = B₄ for
     bosons, where B₄ is the t⁰ heat-trace coefficient including zero modes, and −½B₄[D²_Dirac] for a
     Weyl fermion.
   - The heat traces were computed on S²×S² with radii r₁ ≠ r₂, using the exact S² spectra, and on
     S¹×S³:
     - scalars: l(l+1), multiplicity 2l+1;
     - 1-forms: l(l+1), multiplicity 2(2l+1), l ≥ 1;
     - Dirac D²: n², multiplicity 4n;
     - D² = D₁² + D₂² on the product;
     - S¹×S³ conformal scalar: n², multiplicity n²;
     - S³ Dirac: half-integers m ≥ 3/2, multiplicity 4(m² − ¼);
     - S³ coexact 1-forms: (l+1)², multiplicity 2l(l+2).
   - The small-t expansions were done by exact Euler–Maclaurin series and checked against direct sums to
     10⁻¹⁵ relative error.
   - Every spectrum was also checked against Weyl's law and the first heat coefficient (R/6 − E for
     Laplace-type operators: Lichnerowicz for spinors, Weitzenböck for 1-forms).
   - The Maxwell operator is the Hodge Laplacian on 1-forms minus two Faddeev–Popov scalar ghosts.
   - ∫W², ∫E and ∫R² were computed from the explicit metrics; ∫E = 128π² = 32π²χ on S²×S², and
     W² = E = 0 on S¹×S³.
   - On S²×S², ∫⟨T⟩ = (4c/3 + 4d)(x + 1/x)² − 8a with x = r₂/r₁, which separates a from c + 3d.
     S¹×S³ isolates d.
3. **2D sign check.** On S², the scalar gives B₂ = 1/3 = (1/24π)∫R, and the Dirac fermion gives
   −B₂[D²] = 1/3, i.e. ⟨T⟩ = +cR/24π with c = 1 for each. This is the convention of MMP Eq. (F.29), and
   the fermion value matches MMP's use of c = q for q complex fermions.

**Result: VERIFIED.** The spectral computation returns exactly (check "spectral (zeta) computation on S2xS2
and S1xS3"):
- conformal scalar: {a = 1/360, c = 1/120, d = 0};
- Weyl fermion: {a = 11/720, c = 1/40, d = 0};
- Maxwell: {a = 31/180, c = 1/10, d = 0}.

The heat coefficients on S²×S² are:
- B₄ (conformal scalar) = (r₁⁴ + r₂⁴)/(90r₁²r₂²);
- B₄[D²] (Dirac) = 1/9 − (x² + x⁻²)/15, with x = r₂/r₁;
- B₄ (Maxwell) = −10/9 + 2(x² + x⁻²)/15.

The Ricci-flat traces are, per species:
- scalar: K/2880π²;
- Weyl fermion: 7K/11520π²;
- Maxwell: −13K/2880π².

The normalization matches the local literature exactly. The unit conversions in QUANTUM_ESTIMATES_PASS.md
also reproduce:
- 1.33 ħc/L⁴ = 4.2×10⁻²⁶ J/m³ at 1 m;
- 1.79 c⁴/(GL²) = 2.2×10⁴⁴ Pa at 1 m;
- a photon-to-demand ratio of 0.743 (ℓ_P/L)² = 1.9×10⁻⁷⁰ at 1 m;
- equality at √0.74–√1.64 = 0.86–1.28 ℓ_P;
- neutrino reduced Compton wavelengths of 2 and 20 μm at 0.1 and 0.01 eV.

**Flag (not checkable locally).** Only the scalar coefficients appear in a saved primary text (Ford–Roman
Eq. (10)). The Weyl-fermion and Maxwell values are verified here by an independent computation. Their
standard sources are not saved:
- Christensen–Duff 1978;
- Duff 1994 (abstract only at `T/arx/raw_hep-th_9308075.html`);
- Birrell–Davies.

The zero value of the flat compartment is trivial: all curvature vanishes there.

**Derivation sketch (book).** State the anomaly with its ζ-function origin:
∫√g⟨T^μ_μ⟩ = ζ(0) = (1/16π²)∫√g(cW² − aE) for a boson. Then show the S²×S² computation: the factorized
heat trace K = K₁(t/r₁²)K₂(t/r₂²) with, for the conformal scalar, e^{−τ/3}Θ₀(τ) = 1/τ + 0 + τ/90 + … .
The t⁰ coefficient is (x² + x⁻²)/90, which matches (4c/3)(x² + x⁻² + 2) − 8a only for c = 1/120 and
a = 1/360. The Dirac and Maxwell cases repeat the step.

**Literature checked.**
- `T/inventory/lit_foundations_evidence/gr-qc_9510071.txt` lines 256–279 (Ford–Roman 1996, Eqs. (10),
  (11)).
- `S/wh/txt/1807.04726v3.txt` lines 1643–1684 (MMP App. F, 2D anomaly T^μ_μ = cR/24π) and lines 604–640
  (Eq. (5.25), strip energy −qπ/24L).
- `T/inventory/lit_foundations.md` lines 466–470 (Christensen–Fulling abstract: coefficient (2880π²)⁻¹
  on Schwarzschild; secondary summary).

---

## 5. I25 — Dimensional scaling

**Statement.** Take a demand of fixed shape, g_μν = ĝ_μν(x/L).
- Stresses scale as 1/L²: T = T̂ c⁴/(GL²).
- Integrated energies and contents scale as L, in units of c⁴L/G.
- In Planck units the stress is T̂ (ℓ_P/L)² ρ_P with ρ_P = c⁷/(ħG²), while a quantum field's natural
  stress ħc/L⁴ is (ℓ_P/L)⁴ ρ_P. The quantum-to-demand ratio therefore scales as (ℓ_P/L)².
- Energy per unit length is scale-free: (c⁴/G) × shape factor in J/m, or equivalently **mass** per unit
  length (c²/G) × shape factor.

**Method.**
- Symbolic unit algebra.
- A numerical 1/L² test on a concrete lapse–shift metric with flat slices, depending on t, x and y:
  α = 2 + tanh(x/L)cos(t/L) + 0.3 sin(y/L), β = sin(x/L)e^{−t/L}(1 + 0.2cos(y/L)). The check is that
  L²R(Lx̂) and L²G(n,n)(Lx̂) do not depend on L, for L = 0.01, 7 and 1000 at three points.
- The report's conversions were recomputed.

**Result: VERIFIED WITH A CORRECTED STATEMENT.** The scaling holds to 10⁻²⁶ relative. The inventory
line reads "energy per unit length ∝ c²/G × shape factor". That is the **mass** per unit length;
DEMAND_CENSUS.md quotes it in M_⊙ per metre. The energy per unit length is ∝ c⁴/G.

The numbers check:
- c⁴/G = 1.2103×10⁴⁴ N, so the D-lap peak of 2.9 is 3.5×10⁴⁴ Pa at 1 m;
- the rail unit at the recorded normalization is ℓ_P/√η = 3.29×10⁻³³ m;
- the horizon temperature ħcκ̂/(2πk_B L) is 2.75 mK for κ̂ = 7.55 at 1 m;
- 150 kg at 3.29×10⁻³³ m scales to 2.3×10⁴ M_⊙ at 1 m.

**Corrected statement (book).** For a fixed shape:
- stresses ∝ c⁴/(GL²);
- energies and contents ∝ c⁴L/G;
- energy per unit length ∝ c⁴/G (mass per unit length ∝ c²/G), independent of L;
- quantum stress over demanded stress ∝ (ℓ_P/L)².

**Derivation sketch.** Each coordinate derivative of ĝ(x/L) carries 1/L. Riemann has two derivatives,
so orthonormal curvature ∝ 1/L². Volumes ∝ L³ and lengths ∝ L.

**Literature.** None needed.

---

## 6. Q1–Q13 — Source-physics identities (knobs_throat_era.md §5.4)

In this section, "static spherical" means ds² = −A²dt² + dl² + R²dΩ², with A the lapse (the notation of
the C1 reports), a = log A, and primes for d/dl.

### Q1. Radial 1+1 conformal channels (spherically averaged)

**Statement.** A 2D conformal field of central charge c lives on the static 2D metric −A²dt² + dl², with
reflecting (conformal) boundary conditions at optical separation L = ∫dl/A. In the strip ground state of
the optical time t, the orthonormal stresses are:

  ρ₂ = c[−π/(24L²A²) + (2a″ + a′²)/(24π)],  p₂ = c[−π/(24L²A²) − a′²/(24π)]  (units ħc/length²).

Spread over spheres of area 4πR² and converted with η, these become ρ_Q = ηρ₂/(4πR²),
p_{r,Q} = ηp₂/(4πR²), with p_{t,Q} = 0.

**Method.**
- Apply MMP's Weyl-transformation law (F.29), T = T̂ − (c/12π)[∂ω∂ω − ½ĝ(∂ω)² − ∇̂∇̂ω + ĝ∇̂²ω]. Use
  ω = a in optical coordinates (t, u), du = dl/A, and T̂ the flat strip value −πc/(24L²).
- Derive that strip value from ζ(−1): E₀ = (π/2L)ζ(−1) = −π/(24L).

Checks:
- The trace is (c/24π)R₂ with R₂ = −2A″/A.
- 2D conservation p′ + a′(ρ + p) = 0, and 4D static conservation with p_t = 0.
- Rindler, A = κx: the conformal vacuum equals minus the thermal stress at T_loc = 1/(2πx), with the 2D
  thermal density πcT²/6 derived.
- AdS₂, A = cosh(l/ℓ) with L = πℓ: T ∝ g, with ρ = −p = c/(24πℓ²), as MMP App. F states.
- The strip energy density at L equals the cylinder's at circumference 2L.
- The Killing-energy integrand of C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:172–177 follows.

**Result: VERIFIED.** Hypotheses to state in the book:
1. **Conformal channels.** Each channel is a 2D CFT with conformal boundary conditions at both ends.
2. **The state.** It is the static ground state with respect to the optical time (the conformal vacuum).
3. **Spherical averaging is a modelling assumption.** Setting p_t = 0 describes an ideal longitudinal
   channel. A physical guide supplies its transverse stresses and material reactions separately (the
   report says so). 4D conservation then holds exactly.
4. **η is a design choice.** It is (ℓ_P/L_rail)² at the chosen normalization.

**Derivation sketch (book).** For a static ω(u): T_tt = T̂_tt − (c/24π)ω_u² + (c/12π)ω_uu and
T_uu = T̂_uu − (c/24π)ω_u². With ω_u = A a′ and ω_uu = A²(a″ + a′²), dividing by A² gives ρ₂ and p₂.

**Literature checked.**
- `S/wh/txt/1807.04726v3.txt`: Eqs. (F.28)–(F.29) at lines 1643–1684; Eqs. (5.24)–(5.27) at lines 604–640.
- `S/arx/pdf/0910.5925v2.txt` lines 488–521 (Urban–Olum Eq. (46), the 2D anomalous transformation from
  Birrell–Davies (6.134)). Its null–null part agrees.
- Cardy's review (hep-th/0411189), which the report cites, is not saved.

### Q2. Anomaly lock ρ_Q − p_{r,Q} = ηc(a″ + a′²)/(48π²R²)

**Statement, method.** Subtract the Q1 expressions. Equivalently, ρ − p = −(2D trace)/(4πR²)·η =
−(c/24π)R₂η/(4πR²) with R₂ = −2(a″ + a′²).

**Result: VERIFIED**, and stronger than stated: the combination holds for **every** state of the channels,
because the state-dependent part is traceless in 2D; it is not limited to the strip ground state.
Independence of L is checked. At fixed geometry, ρ + p_r = ηc/(4πR²)[−π/(12L²A²) + a″/(12π)] becomes
more negative as L shrinks.

**Literature.** As for Q1: MMP (F.29) gives T^μ_μ = cR/24π.

### Q3. Reflector reaction and subdivision scaling

**Statement.** Let [p_r]⁺₋ be the jump in radial pressure across a thin reflector. The net radial force
the quantum field exerts on it, which its material must react, is F = −4πR²[p_r]⁺₋. For compartments of
equal optical length and equal c:
- internal walls carry zero net load;
- outer-end loads grow as N² in their Casimir part (the curvature part is independent of N);
- fourfold shortening multiplies the local Casimir part by 16;
- Σc_jL_j is unchanged by repartitioning at fixed population, while Σc_j grows.

**Method.** Momentum balance across the wall, with p from Q1 inserted.

**Result: VERIFIED.** At a right end (field on its − side), the area-integrated load is
−πN²cη/(24A²L²) − cηa′²/(24π), with L the total optical length split into N equal compartments; a left
end carries the opposite sign. Only the Casimir part scales as N².
The sign convention matches Q6: an end with field only on its + side carries −4πR²Δp_r, and one with
field only on its − side carries +4πR²Δp_r.

**Literature.** None needed (momentum conservation).

### Q4. Longitudinal supply bound (weighted integral identity)

**Statement.** In the static spherical class, let the radial quantum channels obey
H_Q ≡ ρ_Q + p_{r,Q} = (k/4πR²)(a″ − C/A²), with k = ηc/12π and C = 4π²/L_opt². This is Q1 for a closed
loop of optical length L_opt with constant total c. Let H_rem be all other radial null stress. With
W = exp[−(R² − R₀²)/2k],

  C∫W/A² dl − (∫WRR″/k dl + [Wa′]⁺₋) = (4π/k)∫WR²H_rem dl,

which is ≥ 0 when H_rem ≥ 0.

**Method.**
- The Einstein equation 8π(ρ + p_r) = (2/R)(a′R′ − R″) was computed from the metric.
- The pointwise identity (4π/k)WR²H_rem = CW/A² − (Wa′)′ − WRR″/k was verified symbolically.
- The closed-loop form of H_Q was checked against Q1.
- The AdS₂×S² control was computed: A = cosh(l/ℓ), R = R₀, L_opt = πℓ, giving S = 8/ℓ, D = 2/ℓ and
  **S/D = 4 exactly**.
- Invariance under A → λA was checked.

**Result: VERIFIED** (identity). The numbers of the gate (4.17%, 0.0799%, 78 of 88 excluded) are
**DESIGN-SPECIFIC**.

**Literature.** None needed; the identity is derived from the stated equations.

### Q5. Conformal scalar on the product R^{1,1} × S² and the curvature-coupling logarithm

**Statement.** For N conformally coupled real scalars in the static vacuum on R^{1,1} × S²_R, with
ℓ = log(R/a₀):

  (ρ, p_r, p_t) = ηN/(2880π²R⁴)·(−2ℓ, 2ℓ, 1 − 2ℓ).

It follows that:
- the radial null projection vanishes;
- the angular null projection is negative for ℓ > 1/4;
- T(ℓ₀) = T(1) − 2(ℓ₀ − 1)H with H = K(1, −1, 1), K = ηN/(2880π²R⁴);
- changing the subtraction convention alone relabels a₀ and adds no stress.

**Method.** Three independent pieces:
1. **The trace.** −ρ + p_r + 2p_t = 2K equals the anomaly (Riem² − Ric²)/(2880π²) = 1/(1440π²R⁴) on this
   background, where W² = 4/(3R⁴).
2. **The log coefficient**, from first principles. Under g → λ²g at fixed renormalization length,
   T^a_b(λ²g) = λ⁻⁴[T^a_b + ln λ (c/16π²)X^a_b], with X^a_b = (2/√g)g_bc δ∫√gW²/δg_ac. X was computed by
   homogeneous (minisuperspace) variations: X = diag(4/3, 4/3, −4/3, −4/3)/R⁴. With c = 1/120 from §4,
   this reproduces exactly the ln(R/a₀) coefficients (−2, 2, −2)K of (ρ, p_r, p_t).
3. **Cross-check with a local text.** X^a_b = −8Z^a_b, where Z^a_b = (∇_c∇^d + ½R_c^d)C^{ca}_{db} is the
   tensor of the anomalous-scaling law T̃ = Ω⁻⁴(T − 8αZ lnΩ). The coefficient is therefore
   α = c/16π² = 1/(1920π²), exactly the scalar value in Kontou 2024, Eqs. (57)–(58).

Point 4 is structural: the general boost-invariant homogeneous tensor with this trace is a particular
solution plus x(−1, 1, −1), and a₀ absorbs x.

**Result: VERIFIED.** The primary source cited by the report is Butcher 2014 (arXiv:1405.1283, Eq. (59)).
It is **not saved locally (flag)**, but every universal element of the formula is verified: the trace,
the log coefficient, the null projections and the linear shift law. The finite part (the value of a₀) is
scheme data, as the report says.

**Literature discrepancy found.** Graham–Olum 2007 (`S/wh/txt/0705.3193v2.txt` lines 151–183) quote
a = 1/(2880π²) for the same anomalous-scaling equation. That is 2/3 of the value consistent with
c = 1/120 and with Kontou's 1/(1920π²). The book should use 1/(1920π²) = c/16π².

**Literature checked.**
- `S/wh/txt/2405.05963v2.txt` lines 810–834 (Kontou, Eqs. (56)–(60)).
- `T/inventory/lit_foundations_evidence/gr-qc_9510071.txt` line 256 ff. (anomaly).
- `S/wh/txt/0705.3193v2.txt`, the discrepant value.

### Q6. Boundary-state response and holding cost

**Statement.**
1. **Dirichlet wall.** At a Dirichlet end of the improved (ξ = 1/6) scalar, where φ and its tangential
   derivatives vanish, the stress is (Δρ, Δp_r, Δp_t) = Δb(1/6, 1/2, −1/6), with b = ⟨(∂_nφ)²⟩.
2. **End interaction.** On the constant cylinder R^{1,1} × S² with conformal coupling, the KK masses are
   m_j = √(j(j+1) + 1/3)/R. The interaction energy of two Dirichlet ends a distance d apart is
   E_int = −(η/2π)Σ_j Σ_{n≥1} (2j+1)(m_j/n) K₁(2n m_j d).
3. **Force ratio.** Each summand satisfies d|F|/|E| = 1 + zK₀(z)/K₁(z) > 1, with z = 2n m_j d.
4. **Holding.** A direct static axial support made of DEC matter needs energy ≥ d|F_int|, so
   E_int + d|F_int| > 0.

**Method.**
- The improved tensor T = T_can − (1/6)(∂∂ − η□)φ² was evaluated at the wall, using φ = x·h(t,x).
- The 1+1 massive Dirichlet Casimir interaction was derived by the Abel–Plana formula,
  E_int = −(d/π)∫_m^∞ √(k² − m²)/(e^{2kd} − 1) dk, and compared with the Bessel series at three (m, d)
  pairs to 10⁻²⁰. Its massless limit is −π/(24d), the Q1 strip value.
- The KK masses follow from the S² spectrum plus R/6 = 1/(3R²).
- The ratio was derived by differentiation, checked numerically, and shown to exceed 1 for all z.

**Result: VERIFIED.**

**Derivation sketch.** Write E_n = −(m/2πn)K₁(z). Since dK₁/dz = −K₀ − K₁/z,
d|dE_n/dd| = |E_n|(1 + zK₀/K₁). DEC gives the support's energy ≥ ∫|p|dV = |F|d.

**Literature.** None needed; derived from first principles.

### Q7. Planar EM Casimir cells and the holding requirement

**Statement.** An ideal EM cell with normal n has (ρ, p_n, p_∥, p_∥) = (−C, −3C, C, C), with
C = ηπ²/(720d⁴). One radial orientation of weight C_r and two angular orientations of weight C_t give

  (ρ, p_r, p_t) = (−C_r − 2C_t, −3C_r + 2C_t, C_r − 2C_t),

with radial and angular null stresses −4C_r and −4C_t. Independently held cells need holder energy
≥ 3(C_r + 2C_t) per volume, and complete cells ≥ 2(C_r + 2C_t).

**Method.** The EM tensor is derived in §2a. Orientations were summed symbolically. The DEC holder must
carry the attractive normal stress 3C of each cell, so its energy density is ≥ 3C per cell; adding the
Casimir energy −(C_r + 2C_t) gives the complete-cell bound.

**Result: VERIFIED.** The hypotheses are ideal plates, homogenization over cells, a DEC holder spanning
the gap, and zero plate mass (plate mass only raises the bound).

**Literature checked.** As §2a (Garattini; MTY). The report's holder source, Costa–Matsas
arXiv:2112.08881, is not saved; the bound is derived here.

### Q8. Shared-field pair cross term

**Statement.** u_E = (Q_L² + Q_R²)/(2R⁴) + Q_LQ_R/R⁴, the field energy of two coaxial populations whose
fluxes Q = R²E add.

**Method, result: VERIFIED.** It equals E²/2 with E = (Q_L + Q_R)/R². This holds in
**Heaviside–Lorentz units**, where ρ_q = Q′/R² and u = E²/2 (the report's Gauss law confirms the unit
system). In Gaussian units u = E²/8π, Q is the charge, and the cross term is Q_LQ_R/(4πR⁴).

The cross term is half the local field energy when Q_L = Q_R. The static Maxwell stress satisfies
∇·T_E = −ρ_q E, the check behind "∇_aT_E^{al̂} = −(F_L + F_R)".

**Literature.** None needed.

### Q9. Scalar-mirror proximity co-scaling

**Statement.** For two finite scalar-mirror layers:
- The interaction energy per area of the quantum scalar is E_I = (1/4π²)∫κ² ln(1 − r₁r₂e^{−2κa}) dκ.
- The attractive traction is F = (1/2π²)∫κ³r₁r₂e^{−2κa}/(1 − r₁r₂e^{−2κa}) dκ.
- With s = d/a and q = g v² a², E_I = −e(q, s)/a³.
- The helpful integrated radial-null coefficient is h_I = 4e − 2q∂_qe.
- The mirrors' opposing coefficient is h_χ = 2qI/(gs), with I = ∫b′² du.
- At fixed (q, s), both h_I and h_χ scale as η/a³.

**Method.**
- The Lifshitz formula was checked in the Dirichlet limit (r₁r₂ = 1 → −π²/(1440a³)) and against
  F = −dE_I/da = 3|E_I|/a.
- Nondimensionalizing the layer mode problem with x = l/a shows the reflection coefficients depend only
  on (κa, q, s).
- Virtual work under a normal-metric scaling l → λl with the fields held fixed gives
  ∫p dl = −λ∂_λE and hence h_I = −a³∫(ρ + p) = 4e − 2q∂_qe.
- ∫χ′² = v²I/d per layer gives h_χ; I = 3.026461769 for the bump b(u) = exp(−u²/(1 − u²)).

**Result: VERIFIED** (structure). The selected (q, s), the crossing coupling g* = 17,385 and the curved
sums are **DESIGN-SPECIFIC**.

**Literature.** None needed.

### Q10. Charged capacitor shells

**Statement.** For a static thin shell between −f dt² + dr²/f + r²dΩ² regions (inner f_in, outer f_out):

  σ = (√f_in − √f_out)/(4πr),  p = (f_out′/√f_out − f_in′/√f_in)/(16π) − σ/2.

For a flat core, a Reissner–Nordström gap of charge Q and a neutral exterior, in the weak field:
- the inner shell carries tension Q²/(16πa³);
- the outer shell carries compression Q²/(16πb³);
- DEC on both shells gives U_E/(M_in + M_out) ≤ 2(b − a)/(b + a).

**Method.**
- K^t_t = f′/(2√f) and K^θ_θ = √f/r were computed for the unit normal √f ∂_r. The Lanczos equation
  S^i_j = −(1/8π)([K^i_j] − δ^i_j[K]) then gives σ and p.
- Weak-field series in ε (M → εM, Q² → εQ²) were taken, with each shell's mass eliminated in favour of
  its σ.
- U_E = (Q²/2)(1/a − 1/b).
- Also checked: the surface conservation y′ = −4π(σ + 2p) and y″ = 8π(1 + 2η)(σ + p)/r with y = 4πrσ,
  and the report's shell potential V = (f_in + f_out)/2 − y²/4 − (f_in − f_out)²/(4y²), obtained by
  squaring y = √(f_in + ȧ²) − √(f_out + ȧ²).

**Result: VERIFIED.**

**Literature checked.** `S/wh/txt/gr-qc_9506083v1.txt` lines 60–150 (Poisson–Visser 1995, Eqs. (6), (8),
(21)–(24)). Their thin-shell wormhole joins two exteriors, so both normals point away from the throat;
for an ordinary shell the square roots enter with opposite signs, as here.

### Q11. Magnetic confinement and the sleeve virial

**Statement.**
1. **Magnetic confinement.** A tangential field confines a plasma of pressure P only if
   B²/8π > P_γ + P_e± (Gaussian), i.e. B²/(2μ₀) in SI.
2. **Sleeve virial.** For a closed-jacket racetrack (two straight legs of length L, bends of radius a) of
   relativistic plasma of energy E, a sleeve of stress-to-energy ratio k needs
   E_sleeve ≥ 2E/(3k(1 + πa/L)).

**Method.**
- The normal Maxwell stress for a tangential field is u = B²/8π, from T_ij = u(δ_ij − 2b_ib_j).
- The units were converted numerically: 1 T gives 3.98×10⁵ J/m³ both ways.
- The thin-cylinder hoop virial ∫σ_θ dV = 2pV_s was derived from σ_θ = pR/t.
- The racetrack volume ratio is V_s/V_core = 2L/(2L + 2πa).
- For radiation, p = E/(3V_core).
- The sleeve stress is bounded by k times its energy density.

**Result:**
- Part 1: **VERIFIED**.
- Part 2: **VERIFIED under its assumptions** (relativistic plasma, thin straight sections, closed jacket
  reacting through the counted sleeves). The factor 1/(1 + πa/L) and the values k ≥ 0.0323 and 0.133
  are **DESIGN-SPECIFIC**.

The analogous sphere benchmark, τ = pR/2 and E_wall ≥ E_γ/2, also checks.

**Literature.** Thompson–Duncan 2001 (the report's source for part 1) and Bousso are not saved. Both
statements are derived here from the Maxwell stress tensor and the Laplace law.

### Q12. Oriented ensembles

**Statement.**
1. **Projector forms** (spatial stress, u = energy density):
   - Maxwell (pure field along b): T_ij = u(δ_ij − 2b_ib_j);
   - ideal sheet (normal a): T_ij = −u(δ_ij − a_ia_j);
   - ideal string (along s): T_ij = −u s_is_j.
2. **Averaging.** Cylindrical averaging maps a local tensor to (u, p_z, (p_θ + p_n)/2).
3. **Example.** A transverse sheet plus a hoop field of unit energies gives (u, p_z, p_θ, p_n) =
   (2, 1, −2, 0).
4. **Bounds.** Suppose tensile materials obey |p_i| ≤ kρ, the other components obey |p_i| ≤ ρ and
   p_θ + p_n ≥ 0, and the total normal stress is zero. Then H ≤ 2kE_m, H ≤ kE_m + E_other and
   E_total ≥ H(1 + k)/(2k).

**Method.**
- The Maxwell tensor (1/4π)(−B_iB_j + ½δ_ijB²) was expanded.
- Nambu–Goto worldvolume tensors T^{μν} = −σh^{μν} were built for the sheet and the string.
- The bounds were proved: H = −(p_θ^m + p_n^m) − (p_θ^o + p_n^o) ≤ 2kE_m; then minimize
  E_m + max(0, H − kE_m) over E_m ≥ H/2k.
- 200,000 random admissible states were sampled (seeded).

**Result: VERIFIED.** The third inequality needs k ≤ 1, the physical range. For k > 1 the minimum is
E_total ≥ H/k.

**Literature.** None needed.

### Q13. Scale invariance of module power

**Statement.** With C_J = (c⁴/G)L_g Ĉ ΔxΔΩ and δ_s = (L_g/c)δ̂:
- C_J/δ_s = (c⁵/G)Ĉ/δ̂ ΔxΔΩ, independent of L_g;
- C_Jδ_s/ħ = (L_g/ℓ_P)² Ĉδ̂ ΔxΔΩ.

**Method, result: VERIFIED** (symbolic unit algebra). c⁵/G = 3.63×10⁵² W.

---

## 7. Items checkable only in part, and literature notes

**Not checkable against a local primary text** (all were verified instead by independent derivation or
computation):
- Weyl-fermion and Maxwell anomaly coefficients: Christensen–Duff 1978, Duff 1994 (abstract only) and
  Birrell–Davies are not saved.
- F(φ)R results: Barceló–Visser 2000 and Butcher 2015 are not saved.
- Butcher 2014, Eq. (59), the cylinder tensor of Q5.
- Brown–Maclay 1969: the EM Casimir tensor is checked instead against Garattini 2019 and MTY 1988.
- Lee et al. 2020 (the 52 μm test of Newtonian gravity), Thompson–Duncan 2001, Costa–Matsas, Cardy's
  review, and the full Dvali texts (abstracts only).

**Not reproducible from the report's inputs:** the faint-tail row of the Q table (window-averaged deficit
not tabulated).

**Literature discrepancies noticed while checking:**
1. **Fewster–Roman 2003, after Eq. III.12:** "variance τ₀" should read "standard deviation τ₀". The
   displayed g and Eq. III.13 are correct with τ₀ the standard deviation.
2. **Graham–Olum 2007 vs Kontou 2024:** the anomalous-scaling coefficient of the conformal scalar is
   quoted as 1/(2880π²) by Graham–Olum and 1/(1920π²) by Kontou. The first-principles value is
   c/16π² = 1/(1920π²).

---

## 8. Summary table

| Item | Statement (short) | Result |
|---|---|---|
| I21-QI 1a | Fewster–Roman Gaussian bound −(u·k)²/(64π²τ₀⁴), τ₀ = standard deviation | VERIFIED |
| I21-QI 1b | N ≥ 64π² d τ₀⁴ (L/ℓ_P)² | VERIFIED WITH HYPOTHESES MADE EXPLICIT (N = minimally coupled scalar count; d window-averaged, u·k = −1; flat-space bound in curved spacetime is Ford–Roman's premise) |
| I21-QI 1c | Q = 0.013 (f = 0.1), 3×10⁻⁶ (f = 0.01) | DESIGN-SPECIFIC; consistent within rounding (faint-tail row not checkable) |
| I21-QI 1d | ℓ* = √Q L (Dvali ℓ* ≈ √N ℓ_P); L ≤ 52 μm/√Q | VERIFIED algebra; ORDER-OF-MAGNITUDE physics (O(1) factors, √(8π) ambiguity; 52 μm not local) |
| I21-Casimir 2a | ideal-mirror null deficit π²ħc/(180a⁴) | VERIFIED for EM; conformal scalar: π²ħc/(360a⁴) |
| I21-Casimir 2b | a = 0.58 √(ℓ_P L) at d_peak = 0.48 | VERIFIED (input design-specific) |
| I21-Casimir 2c | ~10⁷ electron-mirror overhead | ORDER-OF-MAGNITUDE (assumptions 1–5; regimes meet at exactly 4/3) |
| I21-FφR 3a | F″ ≤ 8πT(k,k)F | VERIFIED |
| I21-FφR 3b | F vanishes by ψ's first zero; zeros = bound states; scale-free | VERIFIED WITH HYPOTHESES MADE EXPLICIT (complete ray with flat past ⇒ F′(entry) ≤ 0; resonance edge case); literature cross-check not possible locally |
| I22 | ⟨T⟩ = (cW² − aE)/16π² · ħc/L⁴; (a,c) = (1/360,1/120), (11/720,1/40), (31/180,1/10) | VERIFIED (scalar vs Ford–Roman; all three by independent spectral computation; fermion/vector literature not local) |
| I25 | fixed shape: stress ∝ 1/L², energy ∝ L, SI via c⁴L/G | VERIFIED WITH CORRECTED STATEMENT ("energy per unit length ∝ c²/G" → mass per length ∝ c²/G; energy per length ∝ c⁴/G) |
| Q1 | 1+1 conformal channel stresses | VERIFIED (vs MMP F.29; p_t = 0 is a modelling assumption) |
| Q2 | anomaly lock ρ − p_r = ηc(a″ + a′²)/(48π²R²) | VERIFIED (holds in every state) |
| Q3 | reflector force −4πR²[p_r]; N² end loads; ×16 | VERIFIED |
| Q4 | weighted longitudinal identity; AdS₂ S/D = 4 | VERIFIED (identity); gate numbers DESIGN-SPECIFIC |
| Q5 | conformal scalar on R^{1,1}×S²: (−2ℓ, 2ℓ, 1 − 2ℓ)/(2880π²R⁴) | VERIFIED (trace, log coefficient via c and via Kontou's α; Butcher 2014 not local) |
| Q6 | Dirichlet wall b(1/6,1/2,−1/6); E_int Bessel sum; d\|F\|/\|E\| = 1 + zK₀/K₁ | VERIFIED |
| Q7 | EM cells C = ηπ²/720d⁴; holder ≥ 3(C_r+2C_t), cell ≥ 2(C_r+2C_t) | VERIFIED |
| Q8 | shared-field cross term Q_LQ_R/R⁴ | VERIFIED (Heaviside–Lorentz units) |
| Q9 | h_I, h_χ ∝ η/a³; h_I = 4e − 2q∂_qe | VERIFIED (structure); selected values DESIGN-SPECIFIC |
| Q10 | σ = (√f_in − √f_out)/4πr; U_E/(M_in+M_out) ≤ 2(b−a)/(b+a) | VERIFIED (vs Poisson–Visser) |
| Q11 | B²/8π > P; E_sleeve ≥ 2E/(3k(1+πa/L)) | VERIFIED; sleeve geometry factor DESIGN-SPECIFIC |
| Q12 | projector forms; H ≤ 2kE_m etc. | VERIFIED (k ≤ 1 for the third bound) |
| Q13 | C_J/δ_s ∝ c⁵/G; C_Jδ_s/ħ ∝ (L_g/ℓ_P)² | VERIFIED |
